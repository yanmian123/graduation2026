// 通知类型定义
export interface Notification {
  id: number;
  notification_type: string;
  title: string;
  message: string;
  is_read: boolean;
  related_object_id: number | null;
  related_object_type: string | null;
  created_at: string;
}

// 通知类型的显示名称映射
export const NOTIFICATION_TYPE_NAMES: Record<string, string> = {
  // 企业端通知
  'resume_received': '收到简历',
  'jobseeker_message': '收到求职者私信',
  'system_notification': '系统通知',
  // 求职用户端通知
  'interview_invitation': '面试邀请',
  'application_status_update': '招聘流程更新',
  'company_chat': '企业发起聊天',
  'report_feedback': '举报反馈',
  'post_comment': '帖子评论',
  'user_followed': '被关注',
  'user_message': '用户私信',
  // 通用通知类型
  'system_general': '系统通知',
};

// 通知的图标映射
export const NOTIFICATION_ICONS: Record<string, string> = {
  // 企业端通知
  'resume_received': '📄',
  'jobseeker_message': '💬',
  'system_notification': '📢',
  // 求职用户端通知
  'interview_invitation': '🎯',
  'application_status_update': '📊',
  'company_chat': '💬',
  'report_feedback': '🔍',
  'post_comment': '💬',
  'user_followed': '👥',
  'user_message': '💬',
  // 通用通知类型
  'system_general': '📢',
};