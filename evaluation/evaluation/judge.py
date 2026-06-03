import asyncio
from evaluation.metrics.faithfulness import evaluate_faithfulness
from evaluation.metrics.answer_relevance import evaluate_answer_relevance
from evaluation.metrics.context_precision import evaluate_context_precision
from evaluation.metrics.context_recall import evaluate_context_recall

class EvaluationJudge:
    def __init__(self, client, db, tracer):
        self.client = client
        self.db = db
        self.tracer = tracer

    async def judge(self, run_id, query, answer, context, chunks):
        with self.tracer.start_as_current_span("evaluation.judge") as span:
            f, r, p, c = await asyncio.gather(
                evaluate_faithfulness(query, answer, context, self.client),
                evaluate_answer_relevance(query, answer, self.client),
                evaluate_context_precision(query, chunks, answer, self.client),
                evaluate_context_recall(query, chunks, answer, self.client)
            )
            overall = 0.35*f + 0.30*r + 0.20*p + 0.15*c
            span.set_attribute("faithfulness", f)
            span.set_attribute("answer_relevance", r)
            span.set_attribute("context_precision", p)
            span.set_attribute("context_recall", c)

        # Write to DB
        await self.db.execute("INSERT INTO evaluations(run_id, faithfulness, relevance, precision, recall, overall_score) VALUES (?,?,?,?,?,?)",
                              [run_id, f, r, p, c, overall])

        if overall > 0.8:
            await self.db.execute("INSERT INTO training_pairs(run_id, query, answer, context) VALUES (?,?,?,?)",
                                  [run_id, query, answer, context])
        return overall
