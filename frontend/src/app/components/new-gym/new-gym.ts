import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { WebService } from '../../services/web-service';
import { AuthService } from '../../services/auth-service';

/**
 * The NewGym component provides a form for users to create a new BJJ gym.
 * It collects basic contact information, social media links, and an address
 * which is geocoded into latitude/longitude before being sent to the backend.
 * Only authenticated users may submit a new gym.
 */
@Component({
  selector: 'app-new-gym',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './new-gym.html',
  styleUrl: './new-gym.css',
})
export class NewGym {

  /** Backend error message displayed to the user */
  backendError: string | null = null;

  /** Indicates whether the form is currently being submitted */
  isSubmitting = false;

  /** Reactive form definition for gym creation */
  gymForm: any;

  /**
   * Injects services for form creation, backend API calls,
   * authentication, and navigation.
   */
  constructor(
    private formBuilder: FormBuilder,
    private webService: WebService,
    private auth: AuthService,
    private router: Router
  ) {}

  /**
   * Builds the new gym form with validation rules for contact details,
   * address, and optional social media fields.
   */
  ngOnInit() {
    this.gymForm = this.formBuilder.group({
      name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(80)]],
      address: ['', [Validators.required, Validators.minLength(5)]],
      phone: ['', [Validators.required, Validators.minLength(5), Validators.maxLength(25)]],
      email: ['', [Validators.required, Validators.email]],
      website: [''],
      instagram: [''],
      facebook: [''],
      coaches: ['']
    });
  }

  /** Exposes auth service to templates for convenience */
  get authService() {
    return this.auth;
  }

  /**
   * Checks whether a specific form control is invalid and touched.
   * @param controlName The form control key
   */
  isInvalid(controlName: string) {
    let control = this.gymForm.get(controlName);
    return !!control && control.invalid && control.touched;
  }

  /**
   * Uses the Nominatim API to convert a human-readable address
   * into latitude and longitude coordinates.
   * @throws error if the address cannot be found.
   */
  private geocodeAddress(address: string): Promise<{ lat: number; lon: number }> {
    let url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`;
    return fetch(url)
      .then(res => res.json())
      .then((data: any[]) => {
        if (!data || data.length === 0) {
          throw new Error("Could not find that address. Please try a more specific one.");
        }
        return {
          lat: parseFloat(data[0].lat),
          lon: parseFloat(data[0].lon)
        };
      });
  }

  /**
   * Handles form submission:
   * - validates user authentication
   * - validates the form
   * - geocodes the address
   * - sends the data to the backend
   * - navigates to the new gym’s page upon success
   */
  onSubmit() {
    this.backendError = null;

    if (!this.auth.isLoggedIn()) {
      this.backendError = 'You must be logged in to add a gym.';
      return;
    }

    if (this.gymForm.invalid) {
      this.gymForm.markAllAsTouched();
      return;
    }

    this.isSubmitting = true;

    let formValue = this.gymForm.value;

    this.geocodeAddress(formValue.address)
      .then(coords => {
        let data = {
          name: formValue.name,
          address: formValue.address,
          latitude: coords.lat.toString(),
          longitude: coords.lon.toString(),
          phone: formValue.phone,
          email: formValue.email,
          website: formValue.website,
          instagram: formValue.instagram,
          facebook: formValue.facebook,
          coaches: formValue.coaches ? formValue.coaches.toString() : ""
        };

        this.webService.postGym(data).subscribe({
          next: (response) => {
            this.isSubmitting = false;
            this.gymForm.reset();

            const id = response.id;

            this.router.navigate(['/community']);
          },
          error: (err) => {
            this.isSubmitting = false;
            this.backendError = err.error?.error || 'Something went wrong while creating the gym.';
          }
        });
      })
      .catch(err => {
        this.isSubmitting = false;
        this.backendError = err.message || 'Could not find that address. Please try a different one.';
      });
  }

  /** Cancels the form and navigates back to the gyms list */
  cancel() {
    this.router.navigate(['/community']);
  }
}
