<template>
  <div :id="`comment-${comment.id}`" class="comment-container">
    <n-card bordered class="comment-item">
      <div class="comment-header">
        <n-avatar :src="comment.userAvatar" size="large" round/>
        <div class="comment-user-info">
          <div class="comment-username">
            {{ comment.username }}
            <span v-if="comment.parentUsername" class="reply-info-inline">
              <span class="reply-label">回复</span>
              <span class="reply-target">@{{ comment.parentNickname || comment.parentUsername }}</span>
            </span>
          </div>
          <div class="comment-time">{{ formatTimeAgo(comment.createdAt) }}</div>
        </div>
      </div>
      <div class="comment-content">{{ comment.content }}</div>
      <div class="comment-actions">
        <n-button
          v-if="!comment.isLiked"
          ghost
          size="tiny"
          class="comment-action-btn"
          @click="likeComment(comment.id)"
        >
          <Heart size="14" />
          <span>{{ comment.likeCount }}</span>
        </n-button>
        <n-button
          v-else
          ghost
          size="tiny"
          class="comment-action-btn liked"
          @click="likeComment(comment.id)"
        >
          <Heart size="14" />
          <span>{{ comment.likeCount }}</span>
        </n-button>
        <n-button
          ghost
          size="tiny"
          class="comment-action-btn"
          @click="replyToComment(comment.id)"
        >
          回复
        </n-button>
        <n-dropdown :options="moreOptions" placement="bottom-start" @select="handleMoreAction">
          <n-button ghost size="tiny" class="comment-action-btn">
            ···
          </n-button>
        </n-dropdown>
      </div>
    </n-card>
    
    <div v-if="comment.replies && comment.replies.length > 0">
      <div v-if="isTopLevelComment && !isExpanded" class="expand-replies-btn" @click="toggleExpand">
        <n-button text type="primary">
          <template #icon>
            <ChevronForward />
          </template>
          点击展开 {{ totalRepliesCount }} 条回复
        </n-button>
      </div>
      <div v-else>
        <div class="comment-replies">
          <CommentItem
            v-for="reply in displayedReplies"
            :key="reply.id"
            :comment="reply"
            :article-author-id="articleAuthorId"
            @like="likeComment"
            @reply="replyToComment"
            @delete="deleteComment"
          />
        </div>
        <div v-if="isTopLevelComment && isExpanded" class="collapse-replies-btn" @click="toggleExpand">
          <n-button text>
            <template #icon>
              <ChevronDown />
            </template>
            收起回复
          </n-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { Heart, ChevronForward, ChevronDown } from '@vicons/ionicons5';
import { NCard, NAvatar, NButton, NIcon, NDropdown } from 'naive-ui';

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  articleAuthorId: {
    type: Number,
    default: null
  },
  targetCommentId: {
    type: Number,
    default: null
  }
});

const emit = defineEmits(['like', 'reply', 'delete', 'report']);

const isExpanded = ref(false);
const showAll = ref(false);

const moreOptions = computed(() => {
  const options = [];
  
  const currentUserId = getCurrentUserId();
  console.log('CommentItem - currentUserId:', currentUserId, 'type:', typeof currentUserId);
  console.log('CommentItem - comment.userId:', props.comment.userId, 'type:', typeof props.comment.userId);
  console.log('CommentItem - articleAuthorId:', props.articleAuthorId, 'type:', typeof props.articleAuthorId);
  console.log('CommentItem - comment:', props.comment);
  
  const isCommentAuthor = currentUserId === props.comment.userId;
  const isArticleAuthor = currentUserId === props.articleAuthorId;
  console.log('CommentItem - isCommentAuthor:', isCommentAuthor);
  console.log('CommentItem - isArticleAuthor:', isArticleAuthor);
  console.log('CommentItem - canDelete:', isCommentAuthor || isArticleAuthor);
  
  if (isCommentAuthor || isArticleAuthor) {
    console.log('CommentItem - 添加删除选项');
    options.push({
      label: '删除评论',
      key: 'delete'
    });
  }
  
  options.push({
    label: '举报评论',
    key: 'report'
  });
  
  console.log('CommentItem - moreOptions:', options);
  return options;
});

const isTopLevelComment = computed(() => {
  return !props.comment.parentUsername;
});

const totalRepliesCount = computed(() => {
  const countReplies = (comments) => {
    let count = 0;
    for (const comment of comments) {
      count += 1;
      if (comment.replies && comment.replies.length > 0) {
        count += countReplies(comment.replies);
      }
    }
    return count;
  };
  
  if (!props.comment.replies || props.comment.replies.length === 0) {
    return 0;
  }
  return countReplies(props.comment.replies);
});

const displayedReplies = computed(() => {
  if (isTopLevelComment.value && !isExpanded.value) return [];
  if (isTopLevelComment.value && !showAll.value) return props.comment.replies.slice(0, 3);
  return props.comment.replies;
});

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value;
  if (!isExpanded.value) {
    showAll.value = false;
  }
};

const showAllReplies = () => {
  showAll.value = true;
};

const checkAndExpandTargetComment = (commentId) => {
  if (!commentId) return;
  
  const findAndExpand = (comment) => {
    if (comment.id === commentId) {
      return true;
    }
    
    if (comment.replies && comment.replies.length > 0) {
      for (const reply of comment.replies) {
        if (findAndExpand(reply)) {
          if (!isExpanded.value) {
            isExpanded.value = true;
          }
          if (!showAll.value) {
            showAll.value = true;
          }
          return true;
        }
      }
    }
    
    return false;
  };
  
  findAndExpand(props.comment);
};

watch(
  () => props.targetCommentId,
  (newTargetId) => {
    if (newTargetId) {
      checkAndExpandTargetComment(newTargetId);
    }
  },
  { immediate: true }
);

const formatTimeAgo = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays < 30) return `${diffDays}天前`;
  
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
};

const likeComment = (commentId) => {
  emit('like', commentId);
};

const replyToComment = (commentId) => {
  emit('reply', commentId);
};

const deleteComment = (commentId) => {
  emit('delete', commentId);
};

const handleMoreAction = (key) => {
  if (key === 'delete') {
    deleteComment(props.comment.id);
  } else if (key === 'report') {
    emit('report', props.comment.id);
  }
};

const getCurrentUserId = () => {
  const token = sessionStorage.getItem('accessToken') || sessionStorage.getItem('enterpriseToken');
  console.log('CommentItem - token:', token);
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    console.log('CommentItem - payload:', payload);
    console.log('CommentItem - user_id from payload:', payload.user_id);
    return parseInt(payload.user_id);
  } catch (error) {
    console.error('CommentItem - token解析错误:', error);
    return null;
  }
};
</script>

<style scoped>
.comment-container {
  margin-bottom: 16px;
}

.comment-item {
  padding: 0px;
  margin-bottom: 0px;
}

.comment-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.comment-user-info {
  margin-left: 8px;
}

.comment-username {
  font-weight: 500;
  font-size: 14px;
}

.reply-info-inline {
  margin-left: 8px;
  font-size: 13px;
}

.reply-label {
  color: #86909c;
}

.reply-target {
  color: #165dff;
  font-weight: 500;
}

.comment-time {
  font-size: 12px;
  color: #86909c;
}

.comment-content {
  margin-bottom: 8px;
  line-height: 1.6;
  padding-left: 48px;
}

.comment-actions {
  display: flex;
  gap: 10px;
  padding-left: 48px;
}

.comment-action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #86909c;
  padding: 0;
  height: auto;
}

.comment-action-btn.liked {
  color: #f53f3f;
}

.expand-replies-btn,
.expand-more-btn,
.collapse-replies-btn {
  margin-top: 8px;
  margin-left: 40px;
}

.expand-replies-btn:hover,
.expand-more-btn:hover,
.collapse-replies-btn:hover {
  cursor: pointer;
}

.comment-replies {
  margin-left: 40px;
  margin-top: 8px;
}

.comment-replies .comment-replies {
  margin-left: 0;
}

.comment-replies .comment-item {
  padding: 6px;
  border-left: 2px solid #e8e8e8;
}

.comment-replies .comment-replies .comment-item {
  border-left: none;
  border-top: 1px solid #f0f0f0;
  padding-top: 8px;
  margin-top: 8px;
}
</style>
