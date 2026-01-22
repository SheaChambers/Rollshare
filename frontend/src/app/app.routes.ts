import { Routes } from '@angular/router';
import { AuthComponent } from './components/auth/auth';
import { Techniques } from './components/techniques/techniques';

export const routes: Routes = [
    {
        path: 'login',
        component: AuthComponent
    },
    {
        path: 'techniques',
        component: Techniques
    }
];
