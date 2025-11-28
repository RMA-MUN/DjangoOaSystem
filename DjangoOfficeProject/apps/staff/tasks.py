from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
import logging
import traceback

logger = logging.getLogger(__name__)


@shared_task(name="Send_Email", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def send_email(email: str, subject: str, message: str):
    # 确保每个邮件任务都有一个唯一的ID
    task_id = send_email.request.id
    logger.info(f"开始发送邮件任务: {task_id}, 收件人: {email}, 主题: {subject}")
    try:
        # 发送邮件
        result = send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        logger.info(f"邮件发送成功: {email}, 结果: {result}")
        return result
    except Exception as e:
        # 记录详细错误信息
        logger.error(f"邮件发送失败: {email}, 错误: {str(e)}")
        logger.error(traceback.format_exc())
        # 重新抛出异常以触发重试机制
        raise
    finally:
        logger.info(f"邮件发送任务完成: {email}")
