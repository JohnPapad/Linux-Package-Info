import { Component } from "react"
import DataTable from 'react-data-table-component';
import { withRouter } from 'react-router-dom';
import { orderBy } from 'lodash';
import produce from 'immer';
import { isEqual } from 'lodash';
import { getQueryParams } from '../../utilities/URIutil';
import dpkgSampleData from '../../assets/packageData/dpkg-sample-data.json';


const baseSWHul = "https://archive.softwareheritage.org/browse/";
const columns = [
    {
        name: 'Distribution',
        selector: 'distro',
        sortable: true,
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
    },

    {
        name: "SoftWare Heritage ID",
        selector: "swhid",
        cell: row => <a href={baseSWHul + row.swhid}>{row.swhid}</a>
    }

];

class PackagesList extends Component {

    state = {
        data: dpkgSampleData
    };

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

    render() {

        console.log("packages rendered")

        return (
            <DataTable
                data={[...this.state.data]}
                columns={columns}
                defaultSortField="distro"
                highlightOnHover
                pagination
                sortFunction={this.handleSort}
            />
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
        console.log("Package list should update");
        if (nextProps.location.search !== this.props.location.search){
            return true;
        }

        return !isEqual(this.state.data, nextState.data);
    }

}

export default withRouter(PackagesList);