from flask import current_app
from flask import make_response
from flask import request

from info import constants
from info import redis_store
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha

#图片验证码
@passport_blu.route('/image_code')
def get_image_code():
    """
    1.获取请求参数
    2.生成图片验证码
    3.保存到redis
    4.返回图片验证码
    :return:
    """
    # 1.获取请求参数,args是获取？后面的参数
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")
    # 2.生成图片验证码
    name,text,image_data = captcha.generate_captcha()
    # 3.保存到redis
    try:
        redis_store.set("image_code:%s"%cur_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)
        if pre_id:
            redis_store.delete("image_code:%s"%pre_id)
    except Exception as e:
        current_app.logger.error(e)
    # 4.返回图片验证码
    response = make_response(image_data)
    response.headers['Content-Type']= 'image/jpg'
    return response