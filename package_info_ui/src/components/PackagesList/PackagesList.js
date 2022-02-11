import { Component } from "react"
import DataTable from 'react-data-table-component';
import { withRouter } from 'react-router-dom';
import produce from 'immer';
import { isEqual } from 'lodash';
import SearchForm from '../SearchFilters/SearchFilters';
import { Row, Col, Button, Spinner } from 'reactstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTimesCircle } from '@fortawesome/free-solid-svg-icons';
import { API } from '../../services/API';
import queryString from 'query-string';
import validUrl from 'valid-url';
import { removeHttp, mapDistroToBootstrapColor } from "../../utilities/utilities";
import Versions from "./Versions/Versions";
import { packagesDataTableStyles } from './ContentTableStyles';
import DataTableContextComponent from "../DataTableContextComponent/DataTableContextComponent";


const noDataComponent = (
    <div className="py-3 text-center">
        <p className="mb-0">
            No package found...
        </p>
        <p className="mb-0">
            Please try again with different search criteria
        </p>
    </div>
);

const progressComponent = (
    <div className="my-4">
        <Spinner color="secondary" style={{ width: "4rem", height: "4rem" }}/>
        {/* <p className="text-center mt-2 fst-italic">Loading...</p> */}
    </div>
);


const expandableComponent = (packageInfo, selectedVersion, packageVersionSelectedHandler) => (
    <Versions 
        packageInfo={packageInfo}
        selectedVersion={selectedVersion}
        packageVersionSelectedHandler={packageVersionSelectedHandler}
    />
);


class PackagesList extends Component {

    state = {
        data: [],
        toggleClearSelectedRows: false,
        toggleRerender: false,
        tableResetDefaultPage: true,
        tableIsLoading: true,
        dataTotalCount: 0,
        expandedRowIds: {},
        URLqueryParams: {},
        selectedPackageVersions: {},
        visibleColumns: ['type', 'category', 'rating', 'license', 'maintainer', 'website', 'repo', 'description']
    };

    skipPackagePageChange = false;
    skipRowsChangedTriggering = true;

    selectedPackages = {};

    collectSelectedPackages = (includeSelectedVersion) => {
        let onlyOneDistro = true;
        let prvDistro = null;
        const selectedPackages = [];
        for (const packageId in this.selectedPackages) {
            let packageInfo = {...this.selectedPackages[packageId]};
            if (includeSelectedVersion && (packageId in this.state.selectedPackageVersions)) {
                const selectedVersion = this.state.selectedPackageVersions[packageId];
                packageInfo["selectedVersion"] = selectedVersion;
            }

            if (!prvDistro) {
                prvDistro = packageInfo.distro;
            }
            else if (onlyOneDistro && (prvDistro !== packageInfo.distro)) {
                onlyOneDistro = false;
            }

            selectedPackages.push(packageInfo);
        }

        return {selectedPackages, onlyOneDistro};
    }

    deselectedAllHandler = () => {
        this.selectedPackages = {};
        this.setState(
            produce(draft=>{
                draft.selectedPackageVersions = {};
                draft.toggleClearSelectedRows = !draft.toggleClearSelectedRows;
            })
        );
    }

    deselectedOneHandler = (packageId) => {
        if (packageId in this.selectedPackages) {
            delete this.selectedPackages[packageId];
            this.setState(
                produce(draft=>{
                    draft.toggleClearSelectedRows = !draft.toggleClearSelectedRows;
                })
            );
        }

        if (packageId in this.state.selectedPackageVersions) {
            this.setState(
                produce(draft=>{
                    delete draft.selectedPackageVersions[packageId];
                })
            );
        }
    }

    selectedRowsChangedHandler = state => {
        if (this.skipRowsChangedTriggering) {
            this.skipRowsChangedTriggering = false;
            return;
        }

        console.log("selected rows", state)

        let curSelectedPackages = {};
        for (const selectedPackage of state.selectedRows) {
            curSelectedPackages[selectedPackage.id] = selectedPackage;
        }

        const selectedPackagesCount = Object.keys(this.selectedPackages).length;
        if (state.selectedCount < selectedPackagesCount) { // currently selected packages are less than previously
            // a package was deselected - need to find which one
            let deselectedPackageId = null;
            for (const packageId in this.selectedPackages) { // comparing the previously and currently selected packages
                if (packageId in curSelectedPackages) continue;
                deselectedPackageId = packageId;
                break;
            }

            this.selectedPackages = curSelectedPackages;

            this.setState(
                produce(draft=>{
                    delete draft.selectedPackageVersions[deselectedPackageId];
                })
            );
        }
        else {
            this.selectedPackages = curSelectedPackages;
            this.setState(
                produce(draft=>{
                    draft.toggleRerender = !draft.toggleRerender;
                })
            );
        }
    }

    packageVersionSelectedHandler = (packageInfo, version) => {

        if (version) {
            this.selectedPackages[packageInfo.id] = packageInfo;
        }
        // else if (packageInfo.id in this.selectedPackages) {
        //     delete this.selectedPackages[packageInfo.id];
        // }

        this.setState(
            produce(draft=>{
                if (version) {
                    draft.selectedPackageVersions[packageInfo.id] = version;
                }
                else if (packageInfo.id in draft.selectedPackageVersions) {
                    delete draft.selectedPackageVersions[packageInfo.id];
                }
            })
        );
    }

    getSelectedPackageVersions = (packageId) => {
        return this.state.selectedPackageVersions[packageId];
    }

    omitColumnHandler = (colName) => {
        console.log("col name: ", colName)
        this.setState(
            produce(draft=>{
                draft.visibleColumns = draft.visibleColumns.filter(val=> val !== colName);
            })
        );
    }

    showAllColumnsHandler = () => {
        this.setState(
            produce(draft=>{
                draft.visibleColumns = ['type', 'category', 'rating', 'license', 'maintainer', 'website', 'repo', 'description'];
            })
        );
    }

    onRowExpandToggled = (expanded, row) => {
        console.log("expanded", expanded, "row", row)
        this.setState(
            produce(draft=>{
                if (expanded) {
                    draft.expandedRowIds[row.id] = true;
                }
                else {
                    delete draft.expandedRowIds[row.id];
                }
            })
        );
    }

    handlePackagePageChange = (page) => {
        if (this.skipPackagePageChange) {
            this.skipPackagePageChange = false;
            return;
        }
        const URLqueryParams = {
            ...this.state.URLqueryParams,
            page
        };
        this.fetchPackages(URLqueryParams, true);
    }

    handleSort = (column, sortDirection) => {
        console.log("handle sort: ", column.id, sortDirection)

        let sortingField = column.id;
        if (sortDirection === "desc") {
            sortingField = `-${sortingField}`;
        }

        let orderingFields = [sortingField, 'name', 'distro']
        if (column.id === 'name') {
            orderingFields = [sortingField, 'distro']
        }
        else if (column.id === 'distro') {
            orderingFields = [sortingField, 'name']
        }

        const URLqueryParams = {
            ...this.state.URLqueryParams,
            'page': 1,
            'ordering': orderingFields
        };
        this.skipPackagePageChange = true;
        this.fetchPackages(URLqueryParams);
    }

    render() {

        console.log("-> Packages rendered")

        const visibleColumns = new Set(this.state.visibleColumns);
        const columns = [
            {
                id: 'name',
                name: "Package",
                selector: row => row['name'],
                sortable: true,
                grow: 2,
                wrap: true,
                style: {
                    fontWeight: "500", 
                    fontSize: "110%",
                    color: "#6c757d",
                    paddingTop: "2px",
                    paddingBottom: "4px"
                },
            },
            {
                id: 'distro',
                name: 'Distribution',
                selector: row => row['distro'],
                sortable: true,
                reorder:true,
                grow: 1.5,
                // center: true,
                style: {
                    fontWeight: "500"
                },
                cell: row=>(
                    <div className={`my-auto p-1 border rounded border-${mapDistroToBootstrapColor(row.distro)} text-${mapDistroToBootstrapColor(row.distro)}`}>
                        {row.distro}
                    </div>
                )
            },
        
            {
                id: 'type',
                name: "Type",
                selector: row => row['type'],
                sortable: true,
                reorder:true,
                // center: true,
                width: "85px",
                omit: !visibleColumns.has('type'),
            },
            {
                id: 'section',
                name: "Category",
                selector: row => row['section'],
                sortable: true,
                reorder:true,
                // center: true,
                omit: !visibleColumns.has('category'),
                // grow: 0.5
            },
            {
                id: 'avg_rating',
                name: "Rating",
                selector: row => row['rating'],
                sortable: true,
                reorder:true,
                center: true,
                width: "95px",
                omit: !visibleColumns.has('rating'),
                cell: row=>row.rating ? row.rating.toFixed(1) : "-"
            },

            {
                id: 'license',
                name: "License",
                selector: row => row['license'],
                reorder:true,
                omit: !visibleColumns.has('license'),
                grow: 2,
                wrap: true
            },

            {
                id: 'maintainer',
                name: "Maintainer",
                selector: row => row['maintainer'],
                reorder:true,
                omit: !visibleColumns.has('maintainer'),
                grow: 2.5,
                cell: row=>{
                    if (validUrl.isUri(row.maintainer)) {
                        return <a target="_blank" rel="noreferrer" href={row.maintainer}>{removeHttp(row.maintainer)}</a>;
                    }
                    return <div className="py-1"> {row.maintainer} </div>;
                }
            },

            {
                id: 'homepage',
                name: "Website",
                selector: row => row['homepage'],
                reorder:true,
                omit: !visibleColumns.has('website'),
                grow: 1.5,
                format: row => <a target="_blank" rel="noreferrer" href={row.homepage}>{removeHttp(row.homepage)}</a>
            },
        
            {
                id: 'repo_URL',
                name: "Code Repository",
                selector: row => row['repo_URL'],
                reorder:true,
                omit: !visibleColumns.has('repo'),
                grow: 1.5,
                format: row => <a target="_blank" rel="noreferrer" href={row.repo_URL}>{removeHttp(row.repo_URL)}</a>
            },

            {
                id: 'description',
                name: "Description",
                selector: row => row['description'],
                reorder:true,
                omit: !visibleColumns.has('description'),
                wrap: true,
                grow: 3
            },
        
        ];

        const expandedRowStyles = [
            {
                when: row => this.state.expandedRowIds.hasOwnProperty(row.id),
                style: {
                    backgroundColor: 'rgba(0,0,0,.12)',
                },
            },
        ];

        return (
            <>
            <Row className="mb-4 justify-content-between">
                <Col md="3" className="py-2">
                    <SearchForm fetchPackages={this.fetchPackages}/>
                </Col>
                <Col xs="auto" className="py-2 align-items-center d-flex">
                    <span className="fw-bold me-2">
                        Show: 
                    </span>
                    {
                        this.state.visibleColumns.map(col=>(
                            <span key={col} className="mx-2">
                                <Button color="dark" outline disabled size="sm">
                                    <span className="fw-bold">
                                        {col}
                                    </span>
                                </Button>
                                <FontAwesomeIcon role="button" onClick={()=>this.omitColumnHandler(col)} icon={faTimesCircle} className="mx-2 text-secondary small"/>
                                <span className="py-2" style={{borderLeft: "1px solid grey"}}/>
                            </span>

                        ))
                    }
                    <Button color="secondary" className="ms-2" size="sm" onClick={this.showAllColumnsHandler}>
                        <span className="fw-bold">
                            All
                        </span>
                    </Button>
                </Col>
            </Row>

            <DataTableContextComponent
                selectedPackagesInfo={this.collectSelectedPackages(true)}
                deselectedOneHandler={this.deselectedOneHandler}
                deselectedAllHandler={this.deselectedAllHandler}
            />

            <DataTable
                customStyles={packagesDataTableStyles}
                conditionalRowStyles={expandedRowStyles}
                data={this.state.data}
                columns={columns}
                
                fixedHeader
                persistTableHead
                highlightOnHover
                responsive
                
                noDataComponent={noDataComponent}
                progressPending={this.state.tableIsLoading}
                progressComponent={progressComponent}
                
                pagination
                paginationServer
			    paginationTotalRows={this.state.dataTotalCount}
                paginationPerPage={10}
                paginationResetDefaultPage={this.state.tableResetDefaultPage}
                paginationComponentOptions={{
                    noRowsPerPage: true
                }}
                paginationServerOptions={{
                    persistSelectedOnPageChange: true
                }}
                onChangePage={this.handlePackagePageChange}
                
                expandableRows
                expandOnRowClicked
                expandableRowsComponent={({data})=>expandableComponent(data, this.getSelectedPackageVersions(data.id), this.packageVersionSelectedHandler)}
                onRowExpandToggled={this.onRowExpandToggled}
    
                selectableRows
                selectableRowsHighlight
                onSelectedRowsChange={this.selectedRowsChangedHandler}
                selectableRowSelected={row=>row.id in this.selectedPackages}
                clearSelectedRows={this.state.toggleClearSelectedRows}
                
                sortServer
			    onSort={this.handleSort}
            />
            </>
        );
    }

    fetchPackages = async (URLqueryParams, shouldNotResetTableDefaultPage) => {
        this.setState(
            produce(draft=>{
                draft.tableIsLoading = true;
            })
        );

        const URLqueryString = queryString.stringify(URLqueryParams, {arrayFormat: 'comma'});
        console.log("URLqueryString: ", URLqueryString)

        const response = await API.getPackages(URLqueryString);
        console.log(response);
        this.setState(
            produce(draft=>{
                draft.tableIsLoading = false;
                draft.data = response.results;
                draft.dataTotalCount = response.count;
                draft.URLqueryParams = URLqueryParams;
                draft.selectedPackageVersions = {};
                if (!shouldNotResetTableDefaultPage) {
                    draft.tableResetDefaultPage = !draft.tableResetDefaultPage;
                }
            })
        );
    }

    componentDidMount () {
        console.log("-> Package list did mount");
        const URLqueryParams = {
            'ordering': ['-avg_rating', 'name', 'distro']
        };
        this.fetchPackages(URLqueryParams);
    }

    componentDidUpdate () {
        console.log("-> Package list did update");
    }

    componentWillUpdate () {
        console.log("-> Package list will update");
        this.skipRowsChangedTriggering = true;
    }

}

export default withRouter(PackagesList);