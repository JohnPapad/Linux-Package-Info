import { Component } from "react"
import DataTable from 'react-data-table-component';
import { orderBy } from 'lodash';

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

    distroSortingOrder = "asc";
    packageSortingOrder = "asc";

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

        return (
            <DataTable
                data={[...this.props.data]}
                columns={columns}
                defaultSortField="distro"
                highlightOnHover
                pagination
                sortFunction={this.handleSort}
            />
        );
    }

}

export default PackagesList;