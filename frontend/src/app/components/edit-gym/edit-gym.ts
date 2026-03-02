import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { WebService } from '../../services/web-service';
import { AuthService } from '../../services/auth-service';
import { FormBuilder, Validators, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

/**
 * The EditGym component provides a form for editing an existing
 * BJJ gym profile. This includes updating contact details, social links,
 * and coach listings. The component validates the form, performs
 * reverse geocoding to display an address, and submits changes
 * back to the backend API.
 */
@Component({
  selector: 'app-edit-gym',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './edit-gym.html',
  styleUrl: './edit-gym.css'
})
export class EditGym {

  /** The ID of the gym currently being edited, extracted from the route parameters. */
  gymId!: string;

  /** Reactive form containing gym edit fields. */
  editForm!: FormGroup;

  /** Stores any backend error message returned during an update attempt. */
  backendError: string | null = null;

  /** Determines whether the user is authorised to edit this gym. */
  authorised = false;

  /** Controls the visibility of the delete confirmation modal. */
  confirmDelete = false;

  /**
   * Injects required Angular services for routing, 
   * backend communication, authentication, and form handling.
   *
   * @param route The active route providing access to URL parameters.
   * @param webService The WebService used to communicate with backend gym endpoints.
   * @param auth The AuthService used to check permissions and user identity.
   * @param formBuilder Builds reactive form instances.
   * @param router Used for programmatic navigation post-update.
   */
  constructor(
    private route: ActivatedRoute,
    private webService: WebService,
    private auth: AuthService,
    private formBuilder: FormBuilder,
    private router: Router
  ) {}

  /**
   * Initialises the edit form, loads gym data from the server,
   * checks user permissions, converts existing coaches into display format,
   * and patches values into the form.
   */
  ngOnInit() {
    this.gymId = this.route.snapshot.paramMap.get("id")!;

    this.editForm = this.formBuilder.group({
      name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      address: ['', Validators.required],
      phone: [''],
      email: ['', Validators.email],
      website: [''],
      instagram: [''],
      facebook: [''],
      latitude: [''],
      longitude: [''],
      coaches: ['']
    });

    this.webService.getGym(this.gymId).subscribe({
      next: (gym: any) => {

        // Check authorisation: user must be admin OR gym creator
        this.authorised = this.auth.isAdmin() || gym.created_by === this.auth.getUsername();
        if (!this.authorised) return;

        const lat = gym.geo_location.coordinates[1];
        const lng = gym.geo_location.coordinates[0];

        this.editForm.patchValue({
          name: gym.name,
          address: gym.address || "",
          phone: gym.contact.phone,
          email: gym.contact.email,
          website: gym.contact.website,
          instagram: gym.media_url.instagram,
          facebook: gym.media_url.facebook,
          latitude: lat,
          longitude: lng,
          coaches: gym.coaches?.join(", ") || ""
        });
      }
    });
  }

  /**
   * Checks whether a given form field is both invalid and touched.
   * Used to determine when to show validation feedback.
   *
   * @param field The name of the form control.
   * @returns True if the control is invalid and touched.
   */
  isInvalid(field: string) {
    return this.editForm.get(field)?.invalid && this.editForm.get(field)?.touched;
  }

  /**
   * Submits updated gym information to the backend API.
   *
   * Converts the coach string (e.g. `"Eddie Bravo, Joe Bloggs"`)
   * into an array of individual names before sending.
   *
   * On success, navigates back to the gym's page.
   */
  updateGym() {
    const form = this.editForm.value;

    // Convert comma-separated coach names → array
    const coachArray = form.coaches
      ? form.coaches.split(",").map((c: string) => c.trim()).filter(Boolean)
      : [];

    const payload = {
      name: form.name,
      address: form.address,
      phone: form.phone,
      email: form.email,
      website: form.website,
      instagram: form.instagram,
      facebook: form.facebook,
      coaches: coachArray,
      latitude: form.latitude,
      longitude: form.longitude
    };

    this.webService.editGym(this.gymId, payload).subscribe({
      next: () => this.router.navigate(['/gyms', this.gymId]),
      error: (err) => {
        this.backendError = err.error?.error || "Update failed.";
      }
    });
  }

  /**
   * Opens the delete confirmation modal dialog.
   */
  openDeleteConfirm() {
    this.confirmDelete = true;
  }

  /**
   * Sends a request to delete the gym, if authorised.
   * Navigates back to the gyms list upon successful deletion.
   */
  deleteGym() {
    if (!this.authorised || !this.gymId) return;

    this.webService.deleteGym(this.gymId).subscribe({
      next: () => this.router.navigate(['/community']),
      error: (err) => {
        this.backendError = err.error?.error || "Delete failed.";
      }
    });
  }

  /**
   * Cancels editing and returns to the gym listing page.
   */
  cancel() {
    this.router.navigate(['/gyms', this.gymId]);
  }
}
