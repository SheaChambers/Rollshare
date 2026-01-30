import { Routes } from '@angular/router';
import { AuthComponent } from './components/auth/auth';
import { Techniques } from './components/techniques/techniques';
import { CategoryTechniques } from './components/category-techniques/category-techniques';
import { Technique } from './components/technique/technique';
import { NewTechnique } from './components/new-technique/new-technique';
import { EditTechnique } from './components/edit-technique/edit-technique';
import { authGuard } from './guards/auth-guard-guard';

export const routes: Routes = [
    {
        path: 'login',
        component: AuthComponent
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
        component: EditTechnique
    }
];
