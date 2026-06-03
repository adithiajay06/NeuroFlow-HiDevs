@router.patch("/runs/{run_id}/rating")
async def update_rating(run_id: str, body: dict):
    rating = body["rating"]
    # Update evaluations.user_rating
    await db.execute("UPDATE evaluations SET user_rating=? WHERE run_id=?", [rating, run_id])

    # Compare automated vs human
    row = await db.fetch_one("SELECT overall_score, user_rating FROM evaluations WHERE run_id=?", [run_id])
    if abs(row["overall_score"] - (row["user_rating"]/5)) > 0.3:
        await db.execute("UPDATE evaluations SET metadata=metadata || '{\"calibration_needed\":true}' WHERE run_id=?", [run_id])
    return {"status":"updated"}
