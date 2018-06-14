import random
import re
from datetime import datetime

from flask import current_app, jsonify
from flask import make_response
from flask import request
from flask import session

from info import constants, db
from info import redis_store
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha

#图片验证码
from info.utils.response_code import RET


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

#短信验证码
# 请求路径: /passport/sms_code
# 请求方式: POST
# 请求参数: mobile, image_code,image_code_id
# 返回值: errno, errmsg
@passport_blu.route('/get_msg_code',methods = ['POST'])
def get_msg_code():
    #获得请求过来的三个参数 POST请求
    dict_data = request.json
    mobile = dict_data.get('mobile')
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")
    #校验(内容是否为空)
    if not all([mobile,image_code,image_code_id]):
        return jsonify(error = RET.PARAMERR,errmsg="参数不完整")
    #手机号是否匹配(正则)
    if not re.match('1[356789]\\d{9}',mobile):
        return jsonify(error=RET.DATAERR,errmsg="手机格式不正确")
    #从redis取出图片验证码
    try:
        redis_image_code = redis_store.get("image_code:%s"%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR,errmsg="查找图片验证码失败")
    #判断取出的图片验证码是否过期
    if not redis_image_code:
        return jsonify(error=RET.NODATA,errmsg="图片验证码过期111")
    #比对请求发来的图片验证码和redis的图片验证码
    if image_code.lower() != redis_image_code.lower():
        return jsonify(error=RET.DATAERR,errmsg="图片验证码不正确")
    #生成短信验证码
    msg_code = "%06d"%random.randint(0,999999)
    print(msg_code)

    #调用云通讯发送短信验证码
    # ccp = CCP()
    # result = ccp.send_template_sms(mobile,[msg_code,5],1)
    # if result == -1:
    #     return jsonify(error=RET.THIRDERR,errmsg="短信验证码发送失败")
    #将短信验证码保存到redis
    try:
        redis_store.set("msg_code:%s"%mobile,msg_code,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR ,errmsg="短信保存失败")

    #返回前端
    return jsonify(error=RET.OK,errmsg="短信发送成功")
# 注册模块
@passport_blu.route('/register',methods = ['POST'])
def register():
    # 1.获取三个参数：手机号，短信验证码，密码
    dict_data = request.json
    mobile = dict_data.get('mobile')
    msg_code = dict_data.get('msg_code')
    password = dict_data.get('password')
    # 2.判断是否为空
    if not ([mobile,msg_code,password]):
        return jsonify(error = RET.PARAMERR,errmsg="参数为空")
    # 3.判断手机号是否符合正则匹配
    if not re.match('1[1356789]\\d{9}',mobile):
        return jsonify(error= RET.DATAERR,errmsg = '手机格式不正确')
    # 4.通过手机号取出redis保存的短信验证码
    try:
        redis_msg_code = redis_store.get("msg_code:%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR,errmsg="获取短信验证码异常")
    # 5.判断短信验证码是否过期
    if not redis_msg_code:
        return jsonify(error=RET.NODATA,errmsg="短信验证码过期")
    # 6.比对用户输入与保存短信验证码是否一致
    if msg_code != redis_msg_code:
        return jsonify(error=RET.DATAERR,errmsg = "短信验证码填写错误")
    # 7.创建用户对象，属性
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    #TODO 未加密
    # user.password_hash = password
    #password是user的一个方法，通过property装饰之后可以当做属性调用。
    user.password = password

    # 8.保存数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR,errmsg="数据保存异常")

    # 9.返回到前端
    return jsonify(error=RET.OK,errmsg="注册成功！")

# 登陆 POST请求

@passport_blu.route('/login',methods=["POST"])
def login():
    # 1.获取参数(手机号,密码)
    dict_data = request.json
    mobile = dict_data.get('mobile')
    password = dict_data.get('password')
    # 2.校验(为空,手机正则匹配)
    if not all([mobile,password]):
        return jsonify(error=RET.PARAMERR,errmsg="内容为空")
    # 3.通过手机号取出用户对象
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR,errmsg="数据库查询错误")
    # 4.判断用户对象是否存在
    if not user:
        return jsonify(error=RET.NODATA,errmsg="该用户不存在")
    # 5.判断密码是否正确
    if not user.check_passowrd(password):
        return jsonify(error=RET.DATAERR,errmsg="密码输入错误")
    # 6.记录用户登陆状态
    session['user_id']=user.id
    session['nickname']=user.nick_name
    session['mobile'] = user.mobile
    # 7.记录用户最后登陆时间
    user.last_login = datetime.now()
    # 8.返回前端
    return jsonify(error=RET.OK,errmsg="用户登陆成功")

# 登出,POST请求
@passport_blu.route('/logout', methods=['POST'])
def logout():
    # 清除session
    session.pop("user_id","")
    session.pop("nick_name","")
    session.pop("mobile","")
    return jsonify(error=RET.OK,errmsg = "登出成功！")
    pass