import { Injectable, inject } from '@angular/core';
import { PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root',
})
export class AuthService {

  private platformId = inject(PLATFORM_ID);

  private isBrowser(): Boolean {
    return isPlatformBrowser(this.platformId);
  }

  /**
   * The key used to store the authentication token in sessionStorage.
   */
  private TOKEN_KEY = 'token';

  /**
   * The key used to store the username in sessionStorage.
   */
  private USERNAME_KEY = 'username';
  
  /**
   * Constructor for the AuthService.
   * @param http Injected HttpClient used for HTTP requests.
   * @param router Router used for navigating after login/logout.
   */
  constructor(private http: HttpClient, private router: Router) {}

  /**
   * Attempts to log the user in using the RollShare API.
   * On success, stores the token and username in sessionStorage.
   *
   * @param credentials The user's login details (username and password).
   * @returns An Observable of the API response.
   */
  login(credentials: any) {
    let formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return this.http.post<any>(
      'http://localhost:5001/api/v1.0/login',
      formData
    ).pipe(
      tap(response => {
        sessionStorage.setItem(this.TOKEN_KEY, response.token);
        sessionStorage.setItem(this.USERNAME_KEY, credentials.username);
      })
    );
  }

  /**
   * Logs the user out by removing stored token and username.
   * If the token is expired, the user is redirected with an additional flag.
   *
   * @param expired Whether the logout was triggered by token expiration.
   */
  logout(expired: boolean = false) {
    if (this.isBrowser()) {
      sessionStorage.removeItem(this.TOKEN_KEY);
      sessionStorage.removeItem(this.USERNAME_KEY);
    }

    if (expired) {
      this.router.navigate(['/login'], { queryParams: { expired: true } });
    } else {
      this.router.navigate(['/login']);
    }
  }

  /**
   * Checks whether the user is currently authenticated.
   * Also triggers automatic logout if the token has expired.
   *
   * @returns True if the user is logged in and the token is valid.
   */
  isLoggedIn() {
    if (!this.isBrowser()) return false;

    const token = this.getToken();
    if (!token) return false;

    if (this.isTokenExpired(token)) {
      this.logout(true);
      return false;
    }
    
    return true;
  }

  /**
   * Retrieves the stored username from sessionStorage.
   *
   * @returns The username, or null if not stored.
   */
  getUsername(): string | null {
    if (!this.isBrowser()) return null;
    return sessionStorage.getItem(this.USERNAME_KEY);
  }

  /**
   * Retrieves the stored authentication token from sessionStorage.
   *
   * @returns The token string, or null if not stored.
   */
  getToken(): string | null {
    if (!this.isBrowser()) return null;
    return sessionStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Generates the required HTTP headers for authenticated API requests.
   * Automatically logs the user out if the token is expired.
   *
   * @returns An HttpHeaders object containing the auth token, or an empty header if invalid.
   */
  getAuthHeaders(): HttpHeaders {
    const token = this.getToken();

    if (!token || this.isTokenExpired(token)) {
      this.logout(true);
      return new HttpHeaders();
    }

    return new HttpHeaders({
        'x-access-token': token
    });
  }

  /**
   * Decodes a JWT token and returns its payload.
   *
   * @param token The JWT token to decode.
   * @returns The decoded payload, or null if decoding fails.
   */
  private decodeToken(token: string): any {
    try {
      return JSON.parse(atob(token.split('.')[1]));
    } catch {
      return null;
    }
  }

  /**
   * Checks whether a given token has expired.
   *
   * @param token The JWT token being validated.
   * @returns True if expired, false otherwise.
   */
  private isTokenExpired(token: string): boolean {
    const decoded = this.decodeToken(token);
    if (!decoded || !decoded.exp) return true;

    return Date.now() > (decoded.exp * 1000);
  }

  /**
   * Determines whether the current user has admin privileges
   * by decoding the stored token.
   *
   * @returns True if the user is an admin, false otherwise.
   */
  isAdmin(): boolean {
    const token = this.getToken();
    if (!token) return false;

    const decoded = this.decodeToken(token);
    return decoded?.admin === true;
  }
}
