import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { AuthService } from './auth-service';

/**
 * The Web Service provides access to the endpoints of
 * the RollShare (BJJ) API
 */
@Injectable({
  providedIn: 'root',
})
export class WebService {

  private baseUrl = 'http://192.168.4.25:5001/api/v1.0/';

  /**
   * Creates a new instance of the WebService.
   * @param http The Angular HttpClient used for API requests.
   * @param auth A reference to the AuthService, used for token access.
   */
  constructor(private http: HttpClient, private auth: AuthService) {}

  /**
   * Fetch a page of techniques from the RollShare API
   * @param page The page number requested
   * @param pageSize Number of items per page.
   * @returns An Observable for the collection of techniques
   */
  getTechniques(page: number, pageSize: number = 9) {
    return this.http.get<any>(
      this.baseUrl + 'techniques?pn=' +
      page + '&ps=' + pageSize);
  }

  /**
   * Fetch a single technique by ID.
   * @param id The ID of the technique.
   * @returns An Observable containing the technique object.
   */
  getTechnique(id: string) {
    return this.http.get<any>(
      this.baseUrl + 'techniques/' + id);
  }

  /**
   * Search techniques using a keyword.
   * @param query The text used to filter techniques.
   * @returns An Observable containing matching techniques.
   */
  getTechniquesSearch(query: string) {
    return this.http.get<any>(
      this.baseUrl + 'techniques?q=' + query
    );
  }

  /**
   * Fetch techniques filtered by category and optional advanced filters.
   * @param category The category name (e.g., Guard, Mount).
   * @param page The requested page number.
   * @param pageSize Number of items per page.
   * @param filters Optional search, difficulty, and rating filters.
   * @returns An Observable containing the filtered techniques.
   */
  getTechniquesByCategory(category: string, page: number = 1, pageSize: number = 9, filters: any = {}) {
    let params = new HttpParams()
      .set('category', category)
      .set('pn', page)
      .set('ps', pageSize)
    
      if (filters.q) {
        params = params.set('q', filters.q);
      }

      if (filters.difficulty && filters.difficulty.length) {
        filters.difficulty.forEach((d: string) => {
          params = params.append('difficulty', d);
        });
      }

      if (filters.min_rating) {
        params = params.set('min_rating', filters.min_rating);
      }
    
    return this.http.get<any>(
      this.baseUrl + 'techniques', 
      {params}
    );
  }

  /**
   * Create a new technique.
   * @param technique The technique data submitted from the form.
   * @returns An Observable containing the created technique.
   */
  postTechnique(technique: any) {
    let postData = new FormData();
    postData.append("name", technique.name);
    postData.append("category", technique.category);
    postData.append("difficulty", technique.difficulty);
    postData.append("description", technique.description);
    postData.append("video", technique.videoFile);
    
    return this.http.post<any>(
      this.baseUrl + 'techniques', postData,
      { headers: this.auth.getAuthHeaders() });
  }

  /**
   * Edit an existing technique.
   * @param id The ID of the technique.
   * @param data The updated technique fields.
   * @returns An Observable confirming the update.
   */
  editTechnique(id: string, data: any) {
    let formData = new FormData();
    for (const key in data) {
      formData.append(key, data[key]);
    }

    return this.http.put<any>(
      this.baseUrl + 'techniques/' + id,
      formData, { headers: this.auth.getAuthHeaders() }
    );
  }

  /**
   * Delete a technique by ID.
   * @param id The ID of the technique.
   * @returns An Observable confirming deletion.
   */
  deleteTechnique(id: string) {
    return this.http.delete<any>(
      this.baseUrl + 'techniques/' + id,
      { headers: this.auth.getAuthHeaders() }
    );
  }

  /**
   * Fetch all reviews for a specific technique.
   * @param id The technique ID.
   * @returns An Observable containing the list of reviews.
   */
  getReviews(id: string) {
    return this.http.get<any>(
      this.baseUrl + 'techniques/' + 
      id + '/reviews');
  }

  /**
   * Post a new review for a technique.
   * @param id The technique ID.
   * @param review The review data.
   * @returns An Observable containing the posted review.
   */
  postReview(id: string, review: any) {
    let postData = new FormData();

    postData.append("user", sessionStorage['username']);
    postData.append("rating", review.rating);
    postData.append("comment", review.comment);

    return this.http.post<any>(
      this.baseUrl + 'techniques/' +
      id + '/reviews', postData,
      { headers: this.auth.getAuthHeaders() });
  }

  /**
   * Edit a technique review.
   * @param id The technique ID.
   * @param reviewId The review ID.
   * @param review The updated review content.
   * @returns An Observable confirming the update.
   */
  editReview(id: string, reviewId: string, review: any) {
    const formData = new FormData();
    formData.append("rating", review.rating);
    formData.append("comment", review.comment);

    return this.http.put<any>(
      this.baseUrl + 'techniques/' + id 
      + '/reviews/' + reviewId,
      formData,
      { headers: this.auth.getAuthHeaders() }
    )
  }

  /**
   * Delete a review from a technique.
   * @param id The technique ID.
   * @param reviewId The review ID.
   * @returns An Observable confirming deletion.
   */
  deleteReview(id: string, reviewId: string) {
    return this.http.delete<any>(
      this.baseUrl + 'techniques/' + id
      + '/reviews/' + reviewId,
      { headers: this.auth.getAuthHeaders() }
    );
  }

  /**
   * Fetch a paginated list of gyms with optional filters.
   * @param page The page number requested.
   * @param pageSize Number of gyms per page.
   * @param filters Search, verification, or sort options.
   * @returns An Observable containing the gym list.
   */
  getGyms(page: number = 1, pageSize: number = 9, filters: any = {}) {
    let params = new HttpParams()
      .set('pn', page)
      .set('ps', pageSize);

    if (filters.q) {
      params = params.set('q', filters.q);
    }
    if (filters.verified) {
      params = params.set('verified', filters.verified);
    }
    if (filters.sort_by) {
      params = params.set('sort_by', filters.sort_by);
    }
    if (filters.order) {
      params = params.set('order', filters.order);
    }

    return this.http.get<any>(
      this.baseUrl + 'gyms',
      { params }
    );
  }

  /**
   * Fetch a single gym by ID.
   * @param id The gym ID.
   * @returns An Observable containing the gym object.
   */
  getGym(id: string) {
    return this.http.get<any>(
      this.baseUrl + 'gyms/' + id
    );
  }

  /**
   * Create a new gym.
   * @param gym The gym data from the form.
   * @returns An Observable containing the created gym.
   */
  postGym(gym: any) {
    let formData = new FormData();

    formData.append("name", gym.name);
    formData.append("latitude", gym.latitude);
    formData.append("longitude", gym.longitude);
    formData.append("phone", gym.phone);
    formData.append("email", gym.email);
    
    formData.append("coaches", gym.coaches.toString());

    if (gym.website) {
      formData.append("website", gym.website);
    }
    if (gym.instagram) {
      formData.append("instagram", gym.instagram);
    }
    if (gym.facebook) {
      formData.append("facebook", gym.facebook);
    }

    return this.http.post<any>(
      this.baseUrl + 'gyms',
      formData,
      { headers: this.auth.getAuthHeaders() }
    );
  }

  /**
   * Edit a gym's information.
   * @param id The gym ID.
   * @param data The updated gym fields.
   * @returns An Observable confirming the update.
   */
  editGym(id: string, data: any) {
    let formData = new FormData();
    for (const key in data) {
      formData.append(key, data[key]);
    }

    return this.http.put<any>(
      this.baseUrl + 'gyms/' + id,
      formData, { headers: this.auth.getAuthHeaders() }
    );
  }

  /**
   * Delete a gym by ID.
   * @param id The gym ID.
   * @returns An Observable confirming deletion.
   */
  deleteGym(id: string) {
    return this.http.delete<any>(
      this.baseUrl + 'gyms/' + id,
      { headers: this.auth.getAuthHeaders() }
    );
  }

  /**
   * Upload photos for a gym.
   * @param id The gym ID.
   * @param files An array of image files.
   * @returns An Observable confirming upload.
   */
  uploadGymPhotos(id: string, files: File[]) {
    let formData = new FormData();

    for (let file of files) {
      formData.append('photos', file, file.name);
    }

    return this.http.post(
      this.baseUrl + 'gyms/' + id + '/photos',
      formData, { headers: this.auth.getAuthHeaders() }
    );
  }

  /**
   * Delete a single gym photo.
   * @param id The gym ID.
   * @param photo The filename of the photo to delete.
   * @returns An Observable confirming deletion.
   */
  deleteGymPhoto(id: string, photo: string) {
    return this.http.delete<any>(
      'http://localhost:5001/api/v1.0/gyms/' + id + '/photos',
      { 
        body: { photo }, 
        headers: this.auth.getAuthHeaders()
      }
    );
  }

  /**
   * Fetch all reviews for a gym.
   * @param id The gym ID.
   * @returns An Observable containing the reviews.
   */
  getGymReviews(id: string) {
    return this.http.get<any>(
      this.baseUrl + 'gyms/' + id + '/reviews'
    );
  }

  /**
   * Post a new review for a gym.
   * @param id The gym ID.
   * @param review The review content.
   * @returns An Observable containing the posted review.
   */
  postGymReview(id: string, review: any) {
    let postData = new FormData();

    postData.append("user", sessionStorage['username']);
    postData.append("rating", review.rating);
    postData.append("comment", review.comment);

    return this.http.post<any>(
      'http://localhost:5001/api/v1.0/gyms/' + id + '/reviews',
      postData,
      { headers: this.auth.getAuthHeaders() }
    );
  }

  /**
   * Update an existing gym review.
   * @param id The gym ID.
   * @param reviewId The review ID.
   * @param review The updated review content.
   * @returns An Observable confirming the update.
   */
  editGymReview(id: string, reviewId: string, review: any) {
    const formData = new FormData();
    formData.append("rating", review.rating);
    formData.append("comment", review.comment);

    return this.http.put<any>(
      'http://localhost:5001/api/v1.0/gyms/' + id 
      + '/reviews/' + reviewId,
      formData,
      { headers: this.auth.getAuthHeaders() }
    )
  }

  /**
   * Delete a gym review.
   * @param id The gym ID.
   * @param reviewId The review ID.
   * @returns An Observable confirming deletion.
   */
  deleteGymReview(id: string, reviewId: string) {
    return this.http.delete<any>(
      'http://localhost:5001/api/v1.0/gyms/' + id
      + '/reviews/' + reviewId,
      { headers: this.auth.getAuthHeaders() }
    );
  }

  /**
   * Register a new user account.
   * @param credentials The submitted user registration details.
   * @returns An Observable containing the server response.
   */
  registerUser(credentials: any) {
    let postData = new FormData();
    postData.append("username", credentials.username);
    postData.append("email", credentials.email);
    postData.append("belt_rank", credentials.belt_rank);
    if (credentials.bio) postData.append("bio", credentials.bio);
    postData.append("password", credentials.password);
    postData.append("confirm_password", credentials.confirm_password);

    return this.http.post<any>(
      'http://localhost:5001/api/v1.0/users/register',
      postData
    );
  }

  /**
   * Fetch the currently authenticated user's profile.
   * @returns An Observable containing the user profile.
   */
  getCurrentUser() {
    return this.http.get<any>(
      'http://localhost:5001/api/v1.0/users/me',
      { headers: this.auth.getAuthHeaders() }
    );
  }

  /**
   * Update the current user's profile.
   * @param id The user ID.
   * @param data Updated user fields.
   * @returns An Observable confirming update.
   */
  updateUser(id: string, data: any) {
    let formData = new FormData();
    Object.keys(data).forEach(key => formData.append(key, data[key]));

    return this.http.put<any>(
      'http://localhost:5001/api/v1.0/users/' + id,
      formData,
      { headers: this.auth.getAuthHeaders() }
    );
  }

  /**
   * Delete the authenticated user's account.
   * @param id The user ID.
   * @returns An Observable confirming deletion.
   */
  deleteUser(id: string) {
    return this.http.delete<any>(
      'http://localhost:5001/api/v1.0/users/' + id,
      { headers: this.auth.getAuthHeaders() }
    )
  }

  /**
   * Change the authenticated user's password.
   * @param data Contains the current and new password.
   * @returns An Observable confirming the password update.
   */
  changePassword(data: any) {
    let formData = new FormData();
    formData.append('current_password', data.current_password);
    formData.append('new_password', data.new_password);

    return this.http.put<any>(
      'http://localhost:5001/api/v1.0/users/reset-password',
      formData,
      { headers: this.auth.getAuthHeaders() }
    )
  }
}
