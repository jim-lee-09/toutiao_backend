from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def success_response(message:str="success",data=None): # code默认写死
    content={
        "code":200,
        "message":message,
        "data":data
    }
    # 目标：把任何Fastapi、Pydantic、ORM对象 都要正常响应->code、message、data
    # JSONResponse把HTTP打包成三件套 包含状态码 请求头 请求体
    return JSONResponse(content=jsonable_encoder(content))


