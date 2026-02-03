import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth-service';
import { WebService } from '../../services/web-service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class ProfileComponent implements OnInit {
  isEditing = false;
  profileForm!: FormGroup;
  userData: any;
  showPasswordModal = false;
  passwordForm!: FormGroup;
  showDeleteModal = false;
  backendError: any;

  belt_ranks = ['White Belt', 'Blue Belt', 'Purple Belt', 'Brown Belt', 'Black Belt'];

  constructor(
    public auth: AuthService,
    private webService: WebService,
    private fb: FormBuilder,
    private router: Router
  ) {}

  ngOnInit() {
    this.profileForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      belt_rank: ['']
    });

    this.passwordForm = this.fb.group({
      current_password: ['', Validators.required],
      new_password: ['', [Validators.required, Validators.minLength(6)]]
    });

    this.webService.getCurrentUser().subscribe({
      next: (data: any) => {
        this.userData = data;

        this.profileForm.patchValue({
          username: data.username,
          email: data.email,
          belt_rank: data.belt_rank
        });
      },
      error: (err) => {
        this.backendError = "Unable to fetch profile data";
      }
    });
  }

  /** Checks if a form control is invalid and touched */
  isInvalid(field: string) {
    const control = this.profileForm.get(field);
    return control && control.invalid && control.touched;
  }

  saveChanges() {
    if (this.profileForm.valid) {
      this.webService.updateUser(this.userData._id, this.profileForm.value).subscribe({
        next: () => {
          this.isEditing = false;
        },
        error: (err) => {
          this.backendError = err.error?.error || "Update failed";
        }
      });
    }
  }

  updatePassword() {
    this.webService.changePassword(this.passwordForm.value).subscribe({
      next: () => {
        alert("Password updated!");
        this.auth.logout();
        this.router.navigate(['/login']);
      },
      error: (err) => this.backendError = err.error.error
    });
  }

  logout() {
    this.auth.logout();
    this.router.navigate(['/']);
  }

  deleteAccount() {
    this.auth.logout();
    this.router.navigate(['/']);
  }
}