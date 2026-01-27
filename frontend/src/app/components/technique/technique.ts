import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { WebService } from '../../services/web-service';
import { AuthService } from '../../services/auth-service';

@Component({
  selector: 'app-technique',
  imports: [CommonModule],
  templateUrl: './technique.html',
  styleUrl: './technique.css',
})
export class Technique implements OnInit {
  technique: any;
  reviews: any[] = [];
  activeTab: string = 'reviews';
  videoUrl?: SafeResourceUrl;
  thumbnailUrl?: string;

  constructor(
    private route: ActivatedRoute,
    private sanitiser: DomSanitizer,
    private webService: WebService,
    public auth: AuthService
  ) {}

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadTechniqueData(id);
    }
  }

  loadTechniqueData(id: string) {
    this.webService.getTechnique(id).subscribe(res => {
      this.technique = res;
      if (res.video_blob_url) {
        this.videoUrl = this.sanitiser.bypassSecurityTrustResourceUrl(
          res.video_blob_url
        );
      }

      this.thumbnailUrl = res.thumbnail_blob_url || null;
    });

    this.webService.getReviews(id).subscribe(res => {
      this.reviews = res;
    });
  }

  saveToLibrary() {
    // Placeholder for future implementation
    alert('Technique saved to your library!');
  }

  uploadForAI() {
    // Placeholder for AI video analysis upload
    console.log('Redirecting to AI upload service...');
  }
}