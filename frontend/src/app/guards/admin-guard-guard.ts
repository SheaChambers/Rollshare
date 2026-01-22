import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth-service';

/**
 * Guard that restricts access to routes requiring admin privileges.
 * 
 * This guard ensures that:
 * 1. The user is logged in
 * 2. The user has an admin role (verified through AuthService)
 * 
 * If either condition fails, the user is redirected to the login page.
 */
@Injectable({
  providedIn: 'root'
})
export class adminGuard implements CanActivate {

  /**
   * Injects the authentication service and router.
   *
   * @param auth Service used to verify login and admin status.
   * @param router Router used to redirect unauthorized users.
   */
  constructor(private auth: AuthService, private router: Router) {}

  /**
   * Determines whether the route can be activated.
   * 
   * @returns True only if the user is logged in AND an admin.
   * Otherwise redirects the user to the login page.
   */
  canActivate(): boolean {
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return false;
    }

    if (!this.auth.isAdmin()) {
      this.router.navigate(['/']);
      return false;
    }

    return true;
  }
}
