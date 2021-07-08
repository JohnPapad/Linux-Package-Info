import { Component } from "react"
import DataTable from 'react-data-table-component';
import { withRouter } from 'react-router-dom';
import { orderBy } from 'lodash';
import produce from 'immer';
import { isEqual } from 'lodash';
import { getQueryParams } from '../../utilities/URIutil';
import dpkgSampleData from '../../assets/packageData/dpkg-sample-data.json';
import SearchForm from '../SearchForm/SearchForm';
import { Row, Col, Button } from 'reactstrap';
import ExportOptions from '../ExportOptions/ExportOptions';
import { downloadCSV } from '../../utilities/CSVutil';
import { downloadJSON } from '../../utilities/JSONutil';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faTimesCircle } from '@fortawesome/free-solid-svg-icons'


const baseSWHul = "https://archive.softwareheritage.org/browse/";


class PackagesList extends Component {

    state = {
        data: dpkgSampleData,
        visibleColumns: ['distro', 'version', 'swhid']
    };

    selectedPackages = [];

    exportHandler = (type) => {
        if (type === "CSV") {
            downloadCSV(this.selectedPackages);
        }
        else if (type === "JSON") {
            downloadJSON(this.selectedPackages);
        }
    }

    filterPackages = () => {
        const URLparams = getQueryParams(this.props.location.search);
        if ((!URLparams.distro) || (!URLparams.package)) {
            return;
        }

        this.setState(
            produce(draft=>{
                if (URLparams.distro === "all") {
                    draft.data = dpkgSampleData.filter(item=>item["package"].includes(URLparams.package));
                }
                else {
                    draft.data = dpkgSampleData.filter(item=>item["distro"] === URLparams.distro && item["package"].includes(URLparams.package));
                }
            })
        );
    }

    handleSort = (rows, selector, sortDirection) => {
        // console.log("rows", rows)
        // console.log("selector:", selector)
        // console.log("direction: ", sortDirection)
  
        if (selector === "distro") {
            return [...this.sortByDistro(rows, selector, sortDirection)];
        }
        return orderBy(rows, selector, sortDirection);
    }

    sortByDistro = (rows, selector, sortDirection) => {
        const sortMethod = (rowA, rowB) => {
            if (rowA[selector] < rowB[selector]) {
                return sortDirection === "asc" ? -1 : 1;
            }
            else if (rowA[selector] > rowB[selector]) {
                return sortDirection === "asc" ? 1 : -1;
            }
            
            if (rowA["package"] < rowB["package"]) {
                return -1;
            }
            else if (rowA["package"] > rowB["package"]) {
                return 1;
            }

            if (rowA["version"] < rowB["version"]) {
                return 1;
            }
            else if (rowA["version"] > rowB["version"]) {
                return -1;
            }
            
            return 0;
        } 
        return rows.sort(sortMethod);
    }

    sortByPackage = () => {

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
                draft.visibleColumns = ['distro', 'version', 'swhid'];
            })
        );
    }

    render() {

        console.log("packages rendered")

        const visibleColumns = new Set(this.state.visibleColumns);
        const columns = [
            {
                name: 'Distribution',
                selector: 'distro',
                sortable: true,
                omit: !visibleColumns.has('distro')
            },
        
            {
                name: "Package",
                selector: "package",
                sortable: true,
            },
        
            {
                name: "Version",
                selector: "version",
                sortable: true,
                omit: !visibleColumns.has('version')
            },
        
            {
                name: "SoftWare Heritage ID",
                selector: "swhid",
                omit: !visibleColumns.has('swhid'),
                cell: row => <a href={baseSWHul + row.swhid}>{row.swhid}</a>
            }
        
        ];

        return (
            <>
            <Row className="mb-3 justify-content-between">
                <Col md="3" className="py-2">
                    <SearchForm/>
                </Col>
                <Col xs="auto" className="py-2">
                    <span className="fw-bold me-2">
                        Show: 
                    </span>
                    {
                        this.state.visibleColumns.map(col=>(
                            <span key={col} className="mx-2">
                                <Button color="dark" outline disabled>
                                    <span className="fw-bold">
                                        {col}
                                    </span>
                                </Button>
                                <FontAwesomeIcon role="button" onClick={()=>this.omitColumnHandler(col)} icon={faTimesCircle} className="mx-2 text-secondary small"/>
                                <span className="py-2" style={{borderLeft: "1px solid grey"}}/>
                            </span>

                        ))
                    }
                    <Button color="secondary" className="ms-2" onClick={this.showAllColumnsHandler}>
                        <span className="fw-bold">
                            All
                        </span>
                    </Button>
                </Col>
            </Row>
            <DataTable
                data={[...this.state.data]}
                columns={columns}
                defaultSortField="distro"
                highlightOnHover
                pagination
                responsive
                selectableRows
                selectableRowsHighlight
                sortFunction={this.handleSort}
                onSelectedRowsChange={this.selectedRowsChangedHandler}
                contextActions={<ExportOptions exportHandler={this.exportHandler}/>}
            />
            </>
        );
    }

    componentDidMount () {
        console.log("Package list did mount");
        this.filterPackages();
    }

    componentDidUpdate () {
        console.log("Package list did update");
        this.filterPackages();
    }

    shouldComponentUpdate (nextProps, nextState) {
        if (!isEqual(nextState.visibleColumns, this.state.visibleColumns)) {
            return true;
        }
        console.log("Package list should update");
        if (nextProps.location.search !== this.props.location.search){
            return true;
        }

        return !isEqual(this.state.data, nextState.data);
    }

}

export default withRouter(PackagesList);