import time
import pytest
from fastapi.testclient import TestClient
from main import app 

# FastAPIをテストするためのツール
client = TestClient(app)

def test_fib_performance_and_memoization():
    n = "10000"
    # 1回目のリクエスト
    start_time = time.time()
    response = client.get(f"/fib?n={n}")
    end_time = time.time()
    
    first_duration = end_time - start_time
    assert response.status_code == 200
    print(f"\n[n={n}] 1回目の計算時間: {first_duration:.6f} 秒")

    # 2回目のリクエスト（メモ化が効くはず）
    start_time = time.time()
    response = client.get(f"/fib?n={n}")
    end_time = time.time()
    
    second_duration = end_time - start_time
    print(f"[n={n}] 2回目の計算時間: {second_duration:.6f} 秒")

    # 検証：2回目はメモ化のおかげで劇的に速いはず
    assert second_duration < first_duration
    assert response.json()["status"] == 200

def test_fib_error_handling():
    # 文字列を送った場合
    response = client.get("/fib?n=abc")
    assert response.status_code == 400
    assert response.json()["message"].startswith("Bad request.")

    # 0を送った場合
    response = client.get("/fib?n=0")
    assert response.status_code == 400
    assert "1 or greater" in response.json()["message"]

    # ちゃんと、401であるはずだってテストを書くと、エラーが出る
    # response = client.get("/fib?n=0")
    # assert response.status_code == 401
    # assert "1 or greater" in response.json()["message"]

    # -1を送った場合
    response = client.get("/fib?n=-1")
    assert response.status_code == 400
    assert "1 or greater" in response.json()["message"]
    
    # 1.5を送った場合
    response = client.get("/fib?n=1.5")
    assert response.status_code == 400
    assert "integer" in response.json()["message"]

    # 100,001（上限超え）を送った場合
    response = client.get("/fib?n=100001")
    assert response.status_code == 400
    assert "too large" in response.json()["message"]