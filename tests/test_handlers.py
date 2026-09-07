async def test_check_db(async_client):
    res = await async_client.get("/handlers/check_db")
    assert res.status_code == 200
