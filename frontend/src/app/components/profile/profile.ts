import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, Form } from '@angular/forms';
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
  isEditingSettings = false;
  twoFactorEnabled = false;

  profileForm!: FormGroup;
  settingsForm!: FormGroup;
  passwordForm!: FormGroup;
  twoFaForm!: FormGroup;

  userData: any;
  provisioningUri: string | null = null;
  manualSecret: string | null = null;
  show2FASetup = false;
  twoFactorSetupInProgress = false;
  showPasswordModal = false;
  showDeleteModal = false;
  backendError: any;

  belt_ranks = ['White Belt', 'Blue Belt', 'Purple Belt', 'Brown Belt', 'Black Belt'];
  themes = ['light', 'dark'];

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

    this.settingsForm = this.fb.group({
      theme: ['light'],
      email_notifications: [true],
      profile_visibility: ['public']
    })

    this.twoFaForm = this.fb.group({
      code: ['', [Validators.required, Validators.minLength(6)]]
    });

    this.webService.getCurrentUser().subscribe({
      next: (data: any) => {
        this.userData = data;

        this.profileForm.patchValue({
          username: data.username,
          email: data.email,
          belt_rank: data.belt_rank
        });

        this.settingsForm.patchValue({
          theme: data.settings?.preferences?.theme,
          email_notifications: data.settings?.preferences?.email_notifications,
          profile_visibility: data.settings?.privacy?.profile_visibility ?? 'public'
        });

        const setupOpen = sessionStorage.getItem('2fa_setup_open') === 'true';

        const security = data.settings?.security ?? {};
        this.twoFactorEnabled = security.two_factor_enabled ?? false;

        this.twoFactorSetupInProgress =
          !this.twoFactorEnabled && !!security.two_factor_secret;

        if (setupOpen && this.twoFactorSetupInProgress) {
          this.isEditingSettings = true;
          this.show2FASetup = true;

          this.webService.enable2FA().subscribe({
            next: (response) => {
              this.provisioningUri = response.provisioning_uri;
              const url = new URL(response.provisioning_uri);
              this.manualSecret = url.searchParams.get("secret");
            }
          });
        } else {
          this.show2FASetup = false;
        }
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

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('avatar', file);

    this.webService.uploadAvatar(formData).subscribe({
      next: (res: any) => {
        this.userData.avatar_url = res.avatar_url;
      },
      error: (err) => {
        this.backendError = "Failed to upload image";
      }
    });
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

  saveSettings() {
    this.webService.update_settings(this.settingsForm.value).subscribe({
      next: () => {
        this.isEditingSettings = false;
        console.log("Settings updated");
      },
      error: (err) => {
        this.backendError = err.error?.error || "Update failed";
      }
    });
  }

  start2FASetup() {
    this.webService.enable2FA().subscribe({
      next: (response) => {
        
        this.provisioningUri = response.provisioning_uri;
        
        const url = new URL(response.provisioning_uri);
        this.manualSecret = url.searchParams.get("secret");

        this.show2FASetup = true;
        this.isEditingSettings = true;

        sessionStorage.setItem('2fa_setup_open', 'true');
      },
      error: (err) =>
        this.backendError = err.error?.error || "Could not start 2FA setup"
    });
  }

  verify2FASetup() {
    if (this.twoFaForm.invalid) return;

    this.webService.verify2FASetup(this.twoFaForm.value.code).subscribe({
      next: () => {
        this.twoFactorEnabled = true;
        this.show2FASetup = false;
      },
      error: (err) =>
        this.backendError = err.error?.error || "Invalid code"
    });
  }

  disable2FA() {
    this.webService.disable2FA().subscribe({
      next: () => {
        this.twoFactorEnabled = false;
      },
      error: (err) =>
        this.backendError = err.error?.error || "Could not disable 2FA"
    });
  }

  logout() {
    this.auth.logout();
    this.router.navigate(['/']);
  }

  deleteAccount() {
    this.webService.deleteUser(this.userData._id).subscribe({
      next: () => {
        this.auth.logout();
        this.router.navigate(['/']);
        alert("Account successfully deleted.");
      },
      error: (err) => {
        this.backendError = "Could not delete account. Please try again.";
        console.error(err);
      }
    });
  }
}