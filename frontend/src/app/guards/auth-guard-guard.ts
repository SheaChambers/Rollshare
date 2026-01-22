import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth-service';

/**
 * Guard that restricts access to routes that require a logged-in user.
 * 
 * This guard checks whether the user is authenticated using the AuthService.
 * If the user is not logged in, they are redirected to the login page.
 */
@Injectable({
  providedIn: 'root'
})
export class authGuard implements CanActivate {

  /**
   * Injects the authentication service and Angular router.
   * 
   * @param auth Service used to verify authentication status.
   * @param router Router used to redirect unauthenticated users.
   */
  constructor(private auth: AuthService, private router: Router) {}

  /**
   * Determines whether the route can be activated.
   * 
   * @returns True if the user is logged in, false otherwise.
   * If false, automatically redirects the user to the login page.
   */
  canActivate(): boolean {
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return false;
    }
    return true;
  }
}
