import { Component } from "react"
import DataTable from 'react-data-table-component';
import { withRouter } from 'react-router-dom';
import produce from 'immer';
import { isEqual } from 'lodash';
import SearchForm from '../SearchFilters/SearchFilters';
import { Row, Col, Button, Spinner } from 'reactstrap';
import ExportOptions from '../ExportOptions/ExportOptions';
import { downloadCSV } from '../../utilities/CSVutil';
import { downloadJSON } from '../../utilities/JSONutil';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTimesCircle } from '@fortawesome/free-solid-svg-icons';
import { API } from '../../services/API';
import queryString from 'query-string';
import validUrl from 'valid-url';
import { removeHttp, mapDistroToBootstrapColor } from "../../utilities/utilities";
import VersionsList from "./VersionsLIst/VersionsList";
import { packagesDataTableStyles } from './ContentTableStyles';


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


class PackagesList extends Component {

    state = {
        data: [],
        tableResetDefaultPage: true,
        tableIsLoading: true,
        dataTotalCount: 0,
        expandedRowIds: {},
        URLqueryParams: {},
        visibleColumns: ['type', 'category', 'rating', 'license', 'maintainer', 'website', 'repo', 'description']
    };

    skipPackagePageChange = false;

    selectedPackages = [];

    exportHandler = (type) => {
        if (type === "CSV") {
            downloadCSV(this.selectedPackages);
        }
        else if (type === "JSON") {
            downloadJSON(this.selectedPackages);
        }
    }

    selectedRowsChangedHandler = state => {
        this.selectedPackages = state.selectedRows;
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

        console.log("packages rendered")

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
                grow: 1.2,
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
                width: "80px",
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
            <Row className="mb-3 justify-content-between">
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
            <DataTable
                customStyles={packagesDataTableStyles}
                conditionalRowStyles={expandedRowStyles}
                data={this.state.data}
                columns={columns}
                // defaultSortField="distro"
                fixedHeader
                highlightOnHover
                responsive
                noDataComponent={noDataComponent}
                progressPending={this.state.tableIsLoading}
                // progressComponent={(
                //     <div  style={{height: "15vh", fontSize: "150%"}}>

                //         <Spinner color="secondary" style={{width: "10%"}}/>
                //     </div>
                // )}
                pagination
                paginationServer
			    paginationTotalRows={this.state.dataTotalCount}
                paginationPerPage={10}
                paginationResetDefaultPage={this.state.tableResetDefaultPage}
                paginationComponentOptions={{
                    noRowsPerPage: true
                }}
                onChangePage={this.handlePackagePageChange}
                expandableRows
                expandOnRowClicked
                expandableRowsComponent={({data})=><VersionsList versions={data.versions}/>} 
                selectableRows
                selectableRowsHighlight
                sortServer
			    onSort={this.handleSort}
                onSelectedRowsChange={this.selectedRowsChangedHandler}
                onRowExpandToggled={this.onRowExpandToggled}
                contextActions={<ExportOptions exportHandler={this.exportHandler}/>}
            />
            </>
        );
    }

    fetchPackages = async (URLqueryParams, shouldNotResetTableDefaultPage) => {
        const URLqueryString = queryString.stringify(URLqueryParams, {arrayFormat: 'comma'});
        console.log("URLqueryString: ", URLqueryString)

        const response = await API.getPackages(URLqueryString);
        console.log(response);
        this.setState(
            produce(draft=>{
                draft.tableIsLoading=false;
                draft.data = response.results;
                draft.dataTotalCount = response.count;
                draft.URLqueryParams = URLqueryParams;
                if (!shouldNotResetTableDefaultPage) {
                    draft.tableResetDefaultPage = !draft.tableResetDefaultPage;
                }
            })
        );
    }

    componentDidMount () {
        console.log("Package list did mount");
        const URLqueryParams = {
            'ordering': ['-avg_rating', 'name', 'distro']
        };
        this.fetchPackages(URLqueryParams);
    }

    componentDidUpdate () {
        console.log("Package list did update");
    }

}

export default withRouter(PackagesList);