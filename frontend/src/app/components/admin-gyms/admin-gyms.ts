import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AgGridAngular } from 'ag-grid-angular';
import { ColDef } from 'ag-grid-community';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import { WebService } from '../../services/web-service';
import { BackButton } from '../shared/back-button/back-button';

ModuleRegistry.registerModules([AllCommunityModule]);

@Component({
  selector: 'app-admin-gyms',
  imports: [CommonModule, AgGridAngular, BackButton],
  templateUrl: './admin-gyms.html',
  styleUrl: './admin-gyms.css',
})
export class AdminGyms {
  rowData: any[] = [];

  @ViewChild(AgGridAngular) agGrid!: AgGridAngular;

  pagination = true;
  paginationPageSize = 10;
  paginationPageSizeSelector = [10, 25, 50];

  columnDefs: ColDef[] = [
    { field: "name", flex: 2, filter: true },
    { field: "address", flex: 3, hide: window.innerWidth < 600 },
    { field: "created_by", headerName: "Owner", flex: 1, hide: window.innerWidth < 600 },
    { field: "review_count", headerName: "Reviews", width: 70 },
    {
      field: "verified",
      headerName: "Verified",
      width: 110,
      cellRenderer: (params: any) =>
        params.value ? "Verified" : "Unverified",
      cellStyle: (params: any) => ({
        color: params.value ? "green" : "red",
        fontWeight: "bold"
      })
    },
    {
      headerName: "Actions",
      cellRenderer: (params: any) => {
        const container = document.createElement("div");
        container.style.display = "flex";
        container.style.gap = "8px";

        const verifyBtn = document.createElement("button");
        verifyBtn.innerText = params.data.verified ? "Unverify" : "Verify";
        verifyBtn.className = "btn-primary";

        verifyBtn.onclick = () => this.toggleVerify(params.data);

        const deleteBtn = document.createElement("button");
        deleteBtn.innerText = "Delete";
        deleteBtn.className = "btn-danger";

        deleteBtn.onclick = () => this.deleteGym(params.data._id);

        container.appendChild(verifyBtn);
        container.appendChild(deleteBtn);

        return container;
      }
    }
  ];

  constructor(private webService: WebService, private router: Router) {}

  ngOnInit() {
    this.loadGyms();
  }

  loadGyms() {
    this.webService.getAllAdminGyms().subscribe((data: any) => {
      this.rowData = data;
    });
  }

  deleteGym(id: string) {
    this.webService.deleteGym(id)
    .subscribe(() => {
      const itemToRemove = this.rowData.find(t => t._id === id);
      this.rowData = this.rowData.filter(t => t._id !== id);
      this.agGrid.api.applyTransaction({ remove: [itemToRemove] });
    });
  }

  toggleVerify(gym: any) {

    const request = gym.verified
      ? this.webService.unverifyGym(gym._id)
      : this.webService.verifyGym(gym._id);

    request.subscribe(() => {
      gym.verified = !gym.verified;
      this.agGrid.api.applyTransaction({ update: [{ gym }] });
      this.agGrid.api.refreshCells({ force: true });
    });
  }
}
