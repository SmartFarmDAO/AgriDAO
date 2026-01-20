import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/use-auth';
import { useTranslation } from '@/i18n/config';

interface Post {
  id: number;
  user_id: number;
  content: string;
  image_url?: string;
  likes_count: number;
  comments_count: number;
  created_at: string;
}

interface Comment {
  id: number;
  post_id: number;
  user_id: number;
  content: string;
  created_at: string;
}

export default function Community() {
  const { t } = useTranslation();
  const [posts, setPosts] = useState<Post[]>([]);
  const [newPost, setNewPost] = useState('');
  const [selectedPost, setSelectedPost] = useState<number | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const res = await fetch('http://localhost:8000/social/posts');
      const data = await res.json();
      setPosts(data);
    } catch (error) {
      console.error('Failed to fetch posts:', error);
    }
  };

  const createPost = async () => {
    if (!newPost.trim()) return;
    try {
      const res = await fetch('http://localhost:8000/social/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: newPost }),
      });
      if (res.ok) {
        setNewPost('');
        fetchPosts();
      }
    } catch (error) {
      console.error('Failed to create post:', error);
    }
  };

  const likePost = async (postId: number) => {
    try {
      await fetch(`http://localhost:8000/social/posts/${postId}/like`, {
        method: 'POST',
      });
      fetchPosts();
    } catch (error) {
      console.error('Failed to like post:', error);
    }
  };

  const fetchComments = async (postId: number) => {
    try {
      const res = await fetch(`http://localhost:8000/social/posts/${postId}/comments`);
      const data = await res.json();
      setComments(data);
      setSelectedPost(postId);
    } catch (error) {
      console.error('Failed to fetch comments:', error);
    }
  };

  const addComment = async () => {
    if (!newComment.trim() || !selectedPost) return;
    try {
      const res = await fetch(`http://localhost:8000/social/posts/${selectedPost}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: newComment }),
      });
      if (res.ok) {
        setNewComment('');
        fetchComments(selectedPost);
        fetchPosts();
      }
    } catch (error) {
      console.error('Failed to add comment:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">{t('community.title')}</h1>

      {user && (
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <textarea
            value={newPost}
            onChange={(e) => setNewPost(e.target.value)}
            placeholder={t('community.writePost')}
            className="w-full p-3 border rounded-lg resize-none"
            rows={3}
          />
          <button
            onClick={createPost}
            className="mt-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            {t('community.createPost')}
          </button>
        </div>
      )}

      <div className="space-y-4">
        {posts.map((post) => (
          <div key={post.id} className="bg-white rounded-lg shadow p-4">
            <p className="text-gray-800 mb-3">{post.content}</p>
            {post.image_url && (
              <img src={post.image_url} alt="Post" className="rounded-lg mb-3 max-h-96 object-cover" />
            )}
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <button
                onClick={() => likePost(post.id)}
                className="flex items-center gap-1 hover:text-green-600"
              >
                ❤️ {post.likes_count} {t('community.likes')}
              </button>
              <button
                onClick={() => fetchComments(post.id)}
                className="flex items-center gap-1 hover:text-green-600"
              >
                💬 {post.comments_count} {t('community.comments')}
              </button>
              <span className="text-xs">{new Date(post.created_at).toLocaleDateString()}</span>
            </div>

            {selectedPost === post.id && (
              <div className="mt-4 border-t pt-4">
                <div className="space-y-2 mb-3">
                  {comments.map((comment) => (
                    <div key={comment.id} className="bg-gray-50 p-2 rounded">
                      <p className="text-sm">{comment.content}</p>
                      <span className="text-xs text-gray-500">
                        {new Date(comment.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                </div>
                {user && (
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      placeholder="Add a comment..."
                      className="flex-1 p-2 border rounded"
                    />
                    <button
                      onClick={addComment}
                      className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                    >
                      Comment
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
