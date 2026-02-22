import asyncio
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from functools import lru_cache

app = FastAPI()

# 計算関数
@lru_cache(maxsize=1000)
def calculate_fib(n: int) -> int:
    #n=1, n=2 のときは 1 を返す仕様。
    if n <= 2:
        return 1
    a, b = 1, 1
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b

# 不正な入力の判定と型変換を行う関数
def validate_and_convert(n_str: str | None) -> int:
    # 未入力チェックしたい
    if n_str is None:
        raise ValueError("n is required.")

    #数字であることと、0より大きいかを判定
    if not n_str.isdigit() or n_str == "0":
        raise ValueError("n must be a positive integer (1 or greater).")
    
    #文字列を数値に型変換
    n_int = int(n_str)

    #大きい値が来たときに、チェック
    if n_int > 100000:
        raise ValueError("n is too large. Max allowed is 100000.")
    
    return n_int

# API
@app.get("/fib")
async def get_fibonacci(n: str = Query(None)):
    try:
        # 型変換とバリデーションを実行
        valid_n = validate_and_convert(n)
        
        # 60.0秒タイムアウト
        # ほかにも計算したい場合がある可能性があるから、非同期処理
        result = await asyncio.wait_for(
            asyncio.to_thread(calculate_fib, valid_n), 
            timeout=60.0
        )
        
        #成功した場合
        return {
            "status":  200,
            "result": result
            
            }

    #タイムアウトが起きた場合
    except asyncio.TimeoutError:
        # 60秒を超えたらここに来る
        return JSONResponse(
            status_code=504,
            content={
                "status": 504,
                "message": "Calculation timed out. The request took longer than 60 seconds."
            }
        )
    #入力が悪かった場合
    except ValueError as e:
        # エラーがあった場合、400 Bad Requestを返す
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "message": f"Bad request. {str(e)}"
            }
        )