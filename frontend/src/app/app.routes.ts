import { Routes } from '@angular/router';
import { AuthComponent } from './components/auth/auth';
import { Admin } from './components/admin/admin';
import { Home } from './components/home/home';
import { Techniques } from './components/techniques/techniques';
import { CategoryTechniques } from './components/category-techniques/category-techniques';
import { Technique } from './components/technique/technique';
import { NewTechnique } from './components/new-technique/new-technique';
import { EditTechnique } from './components/edit-technique/edit-technique';
import { authGuard } from './guards/auth-guard-guard';
import { ProfileComponent } from './components/profile/profile';
import { MyTraining } from './components/my-training/my-training';
import { Community } from './components/community/community';
import { NewGym } from './components/new-gym/new-gym';
import { Gym } from './components/gym/gym';
import { EditGym } from './components/edit-gym/edit-gym';
import { adminGuard } from './guards/admin-guard-guard';
import { AdminUsers } from './components/admin-users/admin-users';
import { AdminTechniques } from './components/admin-techniques/admin-techniques';
import { AdminGyms } from './components/admin-gyms/admin-gyms';

export const routes: Routes = [
    {
        path: 'login',
        component: AuthComponent
    },
    {
        path: 'admin',
        component: Admin,
        canActivate: [adminGuard]
    },
    {
        path: '',
        component: Home
    },
    {
        path: 'techniques/new',
        component: NewTechnique,
        canActivate: [authGuard]
    },
    {
        path: 'techniques',
        component: Techniques
    },
    {
        path: 'techniques/category/:category',
        component: CategoryTechniques
    },
    {
        path: 'techniques/:id',
        component: Technique
    },
    {
        path: 'techniques/:id/edit',
        component: EditTechnique,
        canActivate: [authGuard]
    },
    {
        path: 'profile',
        component: ProfileComponent,
        canActivate: [authGuard]
    },
    {
        path: 'training',
        component: MyTraining,
        canActivate: [authGuard]
    },
    {
        path: 'community',
        component: Community
    },
    {
        path: 'gyms/new',
        component: NewGym,
        canActivate: [authGuard]
    },
    {
        path: 'gyms/:id',
        component: Gym
    },
    {
        path: 'gyms/:id/edit',
        component: EditGym,
        canActivate: [authGuard]
    },
    {
        path: 'users',
        component: AdminUsers,
        canActivate: [adminGuard]
    },
    {
        path: 'admin/techniques',
        component: AdminTechniques,
        canActivate: [adminGuard]
    },
    {
        path: 'admin/gyms',
        component: AdminGyms,
        canActivate: [adminGuard]
    }
];
