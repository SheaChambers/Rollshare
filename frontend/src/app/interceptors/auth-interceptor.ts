import { inject } from '@angular/core';
import { HttpInterceptorFn } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth-service';
import { catchError } from 'rxjs/operators';
import { EMPTY, throwError } from 'rxjs';

export const AuthInterceptor: HttpInterceptorFn = (req, next) => {

  const router = inject(Router);
  const auth = inject(AuthService);

  return next(req).pipe(
    catchError((error: any) => {

      if (
        error.status === 403 &&
        error.error?.error === "Account is banned"
      ) {

        sessionStorage.setItem(
          "bannedInfo",
          JSON.stringify({
            banned_at: error.error.banned_at,
            banned_by: error.error.banned_by
          })
        );

        auth.logout();
        router.navigateByUrl('/banned', { replaceUrl: true });

        return EMPTY;
      }

      return throwError(() => error);
    })
  );
};