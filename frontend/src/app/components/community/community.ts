import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebService } from '../../services/web-service';
import { AuthService } from '../../services/auth-service';
import { TechniqueCard } from '../shared/technique-card/technique-card';

@Component({
  selector: 'app-community',
  standalone: true,
  imports: [CommonModule, TechniqueCard],
  templateUrl: './community.html',
  styleUrl: './community.css'
})
export class Community {

  activeTab: 'feed' | 'friends' | 'clubs' = 'feed';
  
  communityPosts: any[] = [];

  currentPage: number = 1;
  pageSize: number = 9;
  
  errorMessage: string | null = null;
  isLoading: boolean = true;

  constructor(
    private webService: WebService,
    public auth: AuthService
  ) {}

  ngOnInit(): void {
    this.loadDiscoveryFeed();
  }

  /**
   * Fetches the global activity feed. 
   * In a real app, you might have a dedicated /community/feed endpoint,
   * but for now, we can fetch all public techniques.
   */
  loadDiscoveryFeed() {
    this.isLoading = true;
    this.webService.getTechniques(this.currentPage, this.pageSize).subscribe({
      next: (response: any) => {
        const data = Array.isArray(response) ? response : response.techniques;

        if (this.auth.isLoggedIn()) {
          this.webService.getSavedTechniques().subscribe({next: (saved) => {
            const savedList = Array.isArray(saved) ? saved : (saved.techniques || []);
            const savedIds = savedList.map((s: any) => s._id);
            
            this.communityPosts = data.map((post: any) => ({
              ...post,
              _id: post._id.toString(),
              isSaved: savedIds.includes(post._id)
            }));
            this.isLoading = false;
          }});
        }
      },
      error: (err) => {
        this.errorMessage = "Failed to load the activity feed.";
        this.isLoading = false;
        console.error(err);
      }
    });
  }

  /**
   * Logic for switching tabs
   */
  switchTab(tab: 'feed' | 'friends' | 'clubs') {
    this.activeTab = tab;
    if (tab === 'feed') {
      this.loadDiscoveryFeed();
    }
    // Logic for 'friends' or 'clubs' would go here later
  }
}