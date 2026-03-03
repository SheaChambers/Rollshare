import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { WebService } from '../../services/web-service';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin.html',
  styleUrls: ['./admin.css']
})
export class Admin {

  overview: any = null;
  topTechniques: any[] = [];
  activeUsers: any[] = [];

  isLoading = true;

  constructor(
    private webService: WebService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadDashboard();
  }

  /**
   * Loads all dashboard data
   */
  loadDashboard() {
    this.isLoading = true;

    this.webService.getAdminOverview().subscribe({
      next: (data) => {
        this.overview = data;
        this.isLoading = false;
      },
      error: () => this.isLoading = false
    });

    this.webService.getTopTechniques().subscribe({
      next: (data) => this.topTechniques = data
    });

  }

  /* ===================== */
  /* MODERATION NAVIGATION */
  /* ===================== */

  goToUsers() {
    this.router.navigate(['/users']);
  }

  goToTechniques() {
    this.router.navigate(['/admin/techniques']);
  }

  goToGyms() {
    this.router.navigate(['/admin/gyms']);
  }

  /* ===================== */
  /* FUTURE MODERATION ACTIONS */
  /* ===================== */

  markTechniqueFeatured(id: string) {
    this.webService.addFeaturedTechnique(id).subscribe(() => {
      this.loadDashboard();
    });
  }

  /*verifyGym(id: string) {
    this.webService.verifyGym(id).subscribe(() => {
      this.loadDashboard();
    });
  }*/

  banUser(id: string) {
    if (!confirm('Are you sure you want to ban this user?')) return;

    this.webService.banUser(id).subscribe(() => {
      this.loadDashboard();
    });
  }

}