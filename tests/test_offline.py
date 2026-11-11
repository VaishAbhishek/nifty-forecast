"""End-to-end run of morning -> re-check -> scorer on a fake internet.

Run:  python3 -m unittest discover -s tests -v
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
TMP = tempfile.mkdtemp(prefix="nf_test_")
os.environ.update(NF_DATA_DIR=TMP, UPSTOX_ANALYTICS_TOKEN="tok-SECRET-123456", TELEGRAM_BOT_TOKEN="999:SECRET-BOT-TOKEN",
                  TELEGRAM_CHAT_ID="424242", ANTHROPIC_API_KEY="sk-SECRET-KEY-abcdef", NF_FAKE_NOW="2026-11-11T09:16:05+05:30")
for k in ("OPENAI_API_KEY", "GEMINI_API_KEY", "LLM_PROVIDER", "LLM_MODEL", "NF_DRY_RUN"):
    os.environ.pop(k, None)

import fake_net  # noqa: E402
from forecast import net, news, quant, run, sentiment, store, strategies, telegram, upstox  # noqa: E402

net.request = fake_net.request
upstox.time.sleep = lambda s: None


def at(ts):
    os.environ["NF_FAKE_NOW"] = ts


def rows(**kw):
    return [r for r in store.load() if all(r.get(k) == v for k, v in kw.items())]


class Pipeline(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TMP, ignore_errors=True)

    def test_1_full_days(self):
        for day in ("2026-11-11", "2026-11-12", "2026-11-13"):
            fake_net.llm_mode["mode"] = "fail" if day == "2026-11-12" else "ok"
            at(day + "T09:16:05+05:30")
            self.assertEqual(run.main(["morning"]), 0)
            ens = rows(date=day, strategy="S9_ensemble")
            self.assertEqual(len(ens), 1)
            self.assertIn(ens[0]["verdict"], ("UP", "DOWN", "QUIET", "NO_TRADE"))
            self.assertTrue(0 <= ens[0]["p_range300"] <= 1)
            self.assertEqual(ens[0]["inputs"]["news_method"], "lexicon" if day == "2026-11-12" else "llm")
            self.assertEqual(run.main(["morning"]), 0)  # second run must not duplicate
            self.assertEqual(len(rows(date=day, strategy="S9_ensemble")), 1)
            at(day + "T09:46:05+05:30")
            self.assertEqual(run.main(["recheck"]), 0)
            self.assertEqual(len(rows(date=day, strategy="R9_recheck")), 1)
            self.assertEqual(len(rows(date=day, strategy="S6_orb")), 1)
            at(day + "T15:45:05+05:30")
            self.assertEqual(run.main(["score"]), 0)
            self.assertTrue(all(r["outcome"] for r in rows(date=day)))
        st = store.read_json("scores.json")
        self.assertEqual(st["sessions"], 3)
        self.assertEqual(st["direction"]["S0_coin"]["calls"], 3)
        truth = fake_net.BY_DATE["2026-11-13"]
        o = rows(date="2026-11-13", strategy="S0_coin")[0]
        self.assertAlmostEqual(o["outcome"]["range_pts"], truth["h"] - truth["l"], places=0)
        self.assertEqual(o["outcome"]["dir_hit"], (truth["c"] > o["open_0915"]) == (o["verdict"] == "UP"))
        self.assertGreaterEqual(len(fake_net.sent_messages), 9)
        morning = [m for m in fake_net.sent_messages if "MORNING CALL" in m][0]
        for section in ("what is driving", "Sentiment", "Technicals", "Sectors", "rules v2"):
            self.assertIn(section, "".join(fake_net.sent_messages), section)
        self.assertIn("Not counted in the tone", morning)

    def test_1b_news_handling(self):
        run_file = store.read_json("runs/2026-11-11_morning.json")
        titles = [h["title"] for h in run_file["headlines"]]
        # the reworded copy of the crude story is merged, not listed twice
        self.assertEqual(sum(1 for t in titles if "crude oil jumps 3%" in t), 1)
        self.assertTrue(any(h["also"] >= 1 for h in run_file["headlines"]))
        kinds = {h["title"]: h["label"]["kind"] for h in run_file["headlines"]}
        self.assertEqual(kinds["Sensex rallies 400 points in early trade"], "market_report")
        self.assertEqual(run_file["sentiment"]["n_reports"], 2)
        self.assertEqual(run_file["sentiment"]["n_relevant"], len(titles) - 2)

    def test_1c_old_rule_versions_are_not_counted(self):
        from forecast import score
        all_rows = store.load()
        fake_old = [dict(r, rule_version="v1", date="2026-11-09") for r in all_rows if r["date"] == "2026-11-11"]
        self.assertEqual(score.stats(all_rows + fake_old, "v2")["sessions"], 3)
        self.assertEqual(score.stats(all_rows + fake_old, "v1")["sessions"], 1)

    def test_2_no_secret_leaks(self):
        blob = "".join(open(os.path.join(d, f)).read() for d, _, fs in os.walk(TMP) for f in fs) + "".join(fake_net.sent_messages)
        for secret in ("tok-SECRET-123456", "999:SECRET-BOT-TOKEN", "sk-SECRET-KEY-abcdef"):
            self.assertNotIn(secret, blob)

    def test_3_holiday_and_weekend_skip(self):
        before = len(store.load())
        for ts in ("2026-11-14T09:16:05+05:30", "2026-11-10T09:16:05+05:30"):
            at(ts)
            self.assertEqual(run.main(["morning"]), 0)
            self.assertEqual(run.main(["recheck"]), 0)
        self.assertEqual(len(store.load()), before)

    def test_4_outside_window_is_not_scored(self):
        at("2026-11-16T11:00:00+05:30")
        self.assertEqual(run.main(["morning"]), 0)
        self.assertEqual(rows(date="2026-11-16"), [])
        self.assertEqual(run.main(["morning", "--force", "--dry-run"]), 0)
        self.assertTrue(all(r["kind"] == "manual" for r in rows(date="2026-11-16")))
        at("2026-11-16T15:45:00+05:30")
        run.main(["score", "--dry-run"])
        self.assertEqual(store.read_json("scores.json")["sessions"], 3)

    def test_5_selftest(self):
        at("2026-11-17T08:00:00+05:30")
        fake_net.llm_mode["mode"] = "ok"
        self.assertEqual(run.main(["selftest"]), 0)
        st = store.read_json("status.json")["selftest"]
        self.assertTrue(st["ok"], [c for c in st["checks"] if not c["ok"]])


class Units(unittest.TestCase):
    def test_llm_garbage_falls_back(self):
        fake_net.llm_mode["mode"] = "garbage"
        s = sentiment.score([{"title": "Sensex crashes as crude spikes", "source": "t"}])
        fake_net.llm_mode["mode"] = "ok"
        self.assertEqual(s["method"], "lexicon")
        self.assertLess(s["score"], 0)

    def test_market_reports_do_not_count(self):
        echo = [{"title": t, "source": "t"} for t in ("Nifty 50 Rises 1.23% at Open on Wednesday",
                                                       "Gift Nifty Up 285 Points; Sensex, Nifty Eye Rally",
                                                       "Nifty expected to open over 300 points higher at 25,340")]
        s = sentiment.score(echo, use_llm=False)
        self.assertEqual((s["score"], s["n_relevant"], s["n_reports"]), (0.0, 0, 3))
        self.assertEqual(strategies.s8_news(s)[0], 0)

    def test_levels_and_option_walls(self):
        days = [{"date": "d%d" % i, "o": 100, "h": 110, "l": 90, "c": 105} for i in range(30)]
        lv = quant.levels(days, 106, 40)
        self.assertAlmostEqual(lv["pivot"], 101.67, places=2)
        self.assertAlmostEqual(lv["r1"], 113.33, places=2)
        self.assertEqual((lv["band_lo"], lv["band_hi"]), (86, 126))

    def test_indicators(self):
        up = [100 + i for i in range(60)]
        self.assertEqual(quant.rsi(up, 14), 100.0)
        self.assertEqual(quant.streak([1, 2, 3, 2, 1, 0]), -3)
        self.assertAlmostEqual(quant.binom_p_one_sided(18, 25), 0.0216, places=3)
        lo, hi = quant.wilson(15, 25)
        self.assertTrue(0.40 < lo < 0.42 and 0.76 < hi < 0.78)

    def test_ensemble_rules(self):
        f = {"gap_pct": 0.1, "prev_close": 100, "ema20": 105, "ema50": 110, "ema200": 120, "rsi2": 50, "streak": 0,
             "range_model": {"p_range": 0.1}}
        neg = {"score": -0.8, "n_relevant": 5, "binary_event_today": None}
        e = strategies.ensemble(f, neg, [])  # gap fade -1, trend -1, news -1
        self.assertEqual(e["verdict"], "DOWN")
        self.assertLessEqual(1 - e["p_up"], 0.60)
        f2 = dict(f, gap_pct=-0.1)  # gap fade now +1, against the news
        self.assertEqual(strategies.ensemble(f2, neg, [])["verdict"], "NO_TRADE")
        hot = {"score": 0.0, "n_relevant": 5, "n_high_impact": 2, "binary_event_today": None}
        self.assertEqual(strategies.ensemble(dict(f, gap_pct=0.0, ema20=95, ema50=90), hot, [])["verdict"], "NO_TRADE")
        flat = {"score": 0.0, "n_relevant": 5, "binary_event_today": None}
        f3 = dict(f, gap_pct=0.0, ema20=95, ema50=90)
        self.assertEqual(strategies.ensemble(f3, flat, [])["verdict"], "QUIET")
        f4 = dict(f3, range_model={"p_range": 0.6})
        self.assertEqual(strategies.ensemble(f4, flat, [])["verdict"], "NO_TRADE")
        self.assertEqual(strategies.ensemble(f, dict(neg, binary_event_today="RBI policy"), [])["verdict"], "NO_TRADE")
        self.assertEqual(strategies.ensemble(f, neg, ["news", "India VIX"])["verdict"], "NO_TRADE")

    def test_recheck_status(self):
        self.assertEqual(strategies.recheck_status("UP", -0.4, None, 100, 0, 0)[0], "INVALIDATED")
        self.assertEqual(strategies.recheck_status("UP", 0.2, None, 100, 0, 0)[0], "STILL VALID")
        self.assertEqual(strategies.recheck_status("DOWN", -0.2, None, 100, 1, 0)[0], "WEAKENED")
        self.assertEqual(strategies.recheck_status("QUIET", 0.0, 0.7, 120, 0, 0)[0], "INVALIDATED")
        self.assertEqual(strategies.recheck_status("NO_TRADE", 0.9, 0.9, 400, 1, 2)[0], "STILL NO TRADE")

    def test_telegram_split(self):
        parts = telegram.split("\n\n".join("para %d " % i + "x" * 900 for i in range(12)))
        self.assertTrue(len(parts) > 1 and all(len(p) <= telegram.LIMIT for p in parts))

    def test_flows_and_dedupe(self):
        fl = news.flows_from_headlines([{"title": "FPIs offload Rs 1,200 crore; DIIs purchased Rs 900 cr", "source": "x"}])
        self.assertEqual((fl["fii_net_cr"], fl["dii_net_cr"]), (-1200.0, 900.0))


if __name__ == "__main__":
    unittest.main()
