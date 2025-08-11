from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

follows_table = Table(
    "follows_table",
    db.Model.metadata,
    Column("follower_id", ForeignKey("user.id"), primary_key=True),
    Column("followed_id", ForeignKey("user.id"), primary_key=True)
)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String(60), nullable=False)
    lastname: Mapped[str] = mapped_column(String(60), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(65), nullable=False)

    following: Mapped[list["User"]] = relationship(
        "User",
        secondary=follows_table,
        primaryjoin=id == follows_table.c.follower_id,
        secondaryjoin=id == follows_table.c.followed_id,
        backref="followers"
    )

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="author")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "followers": [follower.id for follower in self.followers],
            "following": [user.id for user in self.following]
            # do not serialize the password, its a security breach
        }


class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    comment_text: Mapped[str] = mapped_column(String(255), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)

    author: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")

    def serialize(self):
        return {
            "id": self.id,
            "comment_text": self.comment_text,
            "author_id": self.author_id,
            "post_id": self.post_id
        }


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    author: Mapped["User"] = relationship("User", back_populates="posts")

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post")
    media_files: Mapped[list["Media"]] = relationship("Media", back_populates="post")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "comments": [comment.id for comment in self.comments],
            "media": [file.id for file in self.media_files]
        }


class Media(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)

    post: Mapped["Post"] = relationship("Post", back_populates="media_files")

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type,
            "url": self.url,
            "post_id": self.post_id
        }
