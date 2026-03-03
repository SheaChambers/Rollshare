import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AgGridAngular } from 'ag-grid-angular';
import { ColDef } from 'ag-grid-community';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import { WebService } from '../../services/web-service';

ModuleRegistry.registerModules([AllCommunityModule]);

@Component({
  selector: 'app-admin-techniques',
  imports: [CommonModule, AgGridAngular],
  templateUrl: './admin-techniques.html',
  styleUrl: './admin-techniques.css',
})
export class AdminTechniques {
  rowData: any[] = [];

  @ViewChild(AgGridAngular) agGrid!: AgGridAngular;

  pagination = true;
  paginationPageSize = 10;
  paginationPageSizeSelector = [10, 25, 50];

  columnDefs: ColDef[] = [
    { field: "name", flex: 2, minWidth: 120, filter: true },
    { field: "created_by", hide: window.innerWidth < 400, flex: 3 },
    { field: "created_at", hide: window.innerWidth < 400, flex: 3, filter: true },
    {
      headerName: "Actions",
      cellRenderer: (params: any) => {
        const container = document.createElement("div");
        container.style.display = "flex";
        container.style.gap = "10px";

        const viewBtn = document.createElement("button");
        viewBtn.innerText = "View";
        viewBtn.className = "btn-primary";
        viewBtn.onclick = () => this.router.navigate(['/techniques/' + params.data._id]);

        const delBtn = document.createElement("button");
        delBtn.innerText = "Delete";
        delBtn.className = "btn-danger";
        delBtn.onclick = () => this.deleteTechnique(params.data._id);

        container.appendChild(viewBtn);
        container.appendChild(delBtn);
        return container;
      }
    }
  ];

  constructor(private webService: WebService, private router: Router) {}

  ngOnInit() {
    this.loadTechniques();
  }

  loadTechniques() {
    this.webService.getAllAdminTechniques().subscribe((data: any) => {
      this.rowData = data;
    });
  }

  deleteTechnique(id: string) {
    this.webService.deleteTechnique(id)
    .subscribe(() => {
      const itemToRemove = this.rowData.find(t => t._id === id);
      this.rowData = this.rowData.filter(t => t._id !== id);
      this.agGrid.api.applyTransaction({ remove: [itemToRemove] });
    });
  }
}
