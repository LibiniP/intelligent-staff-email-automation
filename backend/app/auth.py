"""Role check.

DEV ONLY: roles come from the X-User / X-Role headers. Before real use, replace
`current_user` with Entra ID (Azure AD) JWT validation and map groups to roles.
"""
import os

from fastapi import Depends, Header, HTTPException

ROLES = {"admin", "hr", "reviewer", "coordinator"}


class User:
    def __init__(self, name: str, role: str):
        self.name, self.role = name, role


def current_user(x_user: str = Header("dev"), x_role: str = Header("admin")) -> User:
    if os.environ.get("AUTH_DEV", "1") != "1":
        raise HTTPException(501, "Entra ID auth not wired yet")
    if x_role not in ROLES:
        raise HTTPException(403, "unknown role")
    return User(x_user, x_role)


def require(*allowed: str):
    def dep(user: User = Depends(current_user)) -> User:
        if user.role != "admin" and user.role not in allowed:
            raise HTTPException(403, f"role '{user.role}' not allowed")
        return user

    return dep
