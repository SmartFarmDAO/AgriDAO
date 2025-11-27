"""Social features API endpoints."""
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from ..database import engine
from ..models import Post, Comment, Like, User


router = APIRouter()


def get_session():
    with Session(engine) as session:
        yield session


class PostCreate(BaseModel):
    content: str
    image_url: str | None = None


class CommentCreate(BaseModel):
    content: str


@router.get("/posts", response_model=List[Post])
def list_posts(
    limit: int = 20,
    session: Session = Depends(get_session),
) -> List[Post]:
    """Get recent posts."""
    query = select(Post).order_by(Post.created_at.desc()).limit(limit)
    return session.exec(query).all()


@router.post("/posts", response_model=Post, status_code=201)
def create_post(
    post_data: PostCreate,
    user_id: int = 1,  # TODO: Get from auth
    session: Session = Depends(get_session),
) -> Post:
    """Create a new post."""
    post = Post(user_id=user_id, content=post_data.content, image_url=post_data.image_url)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.get("/posts/{post_id}/comments", response_model=List[Comment])
def get_comments(
    post_id: int,
    session: Session = Depends(get_session),
) -> List[Comment]:
    """Get comments for a post."""
    query = select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at)
    return session.exec(query).all()


@router.post("/posts/{post_id}/comments", response_model=Comment, status_code=201)
def add_comment(
    post_id: int,
    comment_data: CommentCreate,
    user_id: int = 1,  # TODO: Get from auth
    session: Session = Depends(get_session),
) -> Comment:
    """Add a comment to a post."""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment = Comment(post_id=post_id, user_id=user_id, content=comment_data.content)
    session.add(comment)
    
    post.comments_count += 1
    session.add(post)
    
    session.commit()
    session.refresh(comment)
    return comment


@router.post("/posts/{post_id}/like", status_code=201)
def like_post(
    post_id: int,
    user_id: int = 1,  # TODO: Get from auth
    session: Session = Depends(get_session),
):
    """Like a post."""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if already liked
    existing = session.exec(
        select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already liked")
    
    like = Like(post_id=post_id, user_id=user_id)
    session.add(like)
    
    post.likes_count += 1
    session.add(post)
    
    session.commit()
    return {"message": "Post liked"}


@router.delete("/posts/{post_id}/like")
def unlike_post(
    post_id: int,
    user_id: int = 1,  # TODO: Get from auth
    session: Session = Depends(get_session),
):
    """Unlike a post."""
    like = session.exec(
        select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    ).first()
    
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    post = session.get(Post, post_id)
    if post:
        post.likes_count = max(0, post.likes_count - 1)
        session.add(post)
    
    session.delete(like)
    session.commit()
    return {"message": "Post unliked"}
