from fastapi import APIRouter

from app.api.routes import auth, companies, employees, projects

router = APIRouter()
router.include_router(auth.router)
router.include_router(companies.router)
router.include_router(employees.router)
router.include_router(projects.router)
