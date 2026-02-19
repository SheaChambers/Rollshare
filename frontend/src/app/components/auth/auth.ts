import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth-service';
import { WebService } from '../../services/web-service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './auth.html',
  styleUrl: './auth.css',
})
export class AuthComponent implements OnInit {
  authForm!: FormGroup;
  twoFaForm!: FormGroup;

  isLoginMode = true;
  requires2FA = false;
  tempUsername: string | null = null;

  backendError: string | null = null;
  sessionExpired = false;

  constructor(
    private fb: FormBuilder,
    private auth: AuthService,
    private webService: WebService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.initForm();

    this.twoFaForm = this.fb.group({
      code: ['', [Validators.required, Validators.minLength(6)]]
    });

    this.route.queryParams.subscribe(params => {
      if (params['expired']) this.sessionExpired = true;
    });
  }

  private initForm() {
    this.authForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      email: [''], 
      belt_rank: [''],
      confirm_password: ['']
    }, { validators: this.passwordMatchValidator });

    this.updateValidators();
  }

  toggleMode() {
    this.isLoginMode = !this.isLoginMode;
    this.backendError = null;
    this.updateValidators();
  }

  private updateValidators() {
    const emailControl = this.authForm.get('email');
    const beltControl = this.authForm.get('belt_rank');
    const confirmControl = this.authForm.get('confirm_password');

    if (this.isLoginMode) {
      emailControl?.clearValidators();
      beltControl?.clearValidators();
      confirmControl?.clearValidators();
    } else {
      emailControl?.setValidators([Validators.required, Validators.email]);
      beltControl?.setValidators([Validators.required]);
      confirmControl?.setValidators([Validators.required]);
    }
    
    emailControl?.updateValueAndValidity();
    beltControl?.updateValueAndValidity();
    confirmControl?.updateValueAndValidity();
  }

  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password')?.value;
    const confirm = form.get('confirm_password')?.value;

    return password && confirm && password !== confirm
      ? { passwordMismatch: true }
      : null;
  }

  /**
   * Checks whether a specific form control is invalid and touched.
   * @param control The name of the control
   */
  isInvalid(control: string) {
    return this.authForm.controls[control].invalid &&
           this.authForm.controls[control].touched;
  }

  onSubmit() {
    this.backendError = null;
    const formData = this.authForm.value;

    if (this.isLoginMode) {
      this.auth.login({ username: formData.username, password: formData.password }).subscribe({
        next: (response: any) => {

          if (response.required_2fa) {
            this.requires2FA = true;
            this.tempUsername = formData.username;
            return;
          }
          
          this.router.navigate(['/techniques']);
        },
        error: (err) => this.backendError = err.error?.error || "Invalid credentials"
      });
    } else {
      this.webService.registerUser(formData).subscribe({
        next: () => {
            this.isLoginMode = true;
            this.updateValidators();
        },
        error: (err) => this.backendError = err.error?.error || "Registration failed"
      });
    }
  }

  verify2FA() {
    if (this.twoFaForm.invalid || !this.tempUsername) return;

    this.auth.verify2FA({
      username: this.tempUsername,
      code: this.twoFaForm.value.code
    }).subscribe({
      next: () => {
        this.router.navigate(['/techniques']);
      },
      error: (err) =>
        this.backendError = err.error?.error || "Invalid 2FA code"
    });
  }
}