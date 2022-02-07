import { Component } from "react"
import DataTable from 'react-data-table-component';
import { withRouter } from 'react-router-dom';
import produce from 'immer';
import { isEqual } from 'lodash';
import { Row, Col, Input } from 'reactstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { API } from '../../../services/API';
import { removeHttp } from '../../../utilities/utilities';
import pretty from 'prettysize';
import { versionsDataTableStyles } from '../ContentTableStyles';


class VersionsList extends Component {

    state = {
        data: this.props.versions
    };

    rateHandler = async (rate, packageVersionId) => {
        alert(rate);
        const payload = {
            rate: Number(rate),
            pkg_version: packageVersionId,
            user: 2
        };

        console.log("rate version payload: ", payload)
        const responseStatus = await API.ratePackageVersion(payload);
        if (responseStatus === 201) {

        }

    }

    render() {
        const isAuth = true;
        const hasVoted = false;
        console.log("versions state: ", this.state)

        console.log("versions rendered")
        const columns = [
            {
                name: "Version",
                selector: row => row['version'],
                sortable: true,
                // grow: 1.5,
                // format: row => <span style={{fontWeight: "500"}}>{row.version}</span>
            },
            {
                name: 'Architecture',
                selector: row => row['architecture'],
                reorder:true,
                center: true,
                grow: 0.75
            },
            {
                name: "Size",
                selector: row => row['size'],
                sortable: true,
                reorder:true,
                grow: 0.5,
                center: true,
                format: row=>pretty(row.size)
            },
            {
                name: "Rating",
                selector: row => row['rating'],
                sortable: true,
                reorder:true,
                grow: 0.5,
                center: true,
                cell: row=>row.rating ? row.rating.toFixed(1) : "-"
            },
            {
                name: "Rate",
                reorder:true,
                omit: !isAuth,
                grow: 0.5,
                center: true,
                cell: row=>(
                    <Input
                        type="select"
                        bsSize="sm"
                        className="my-1 mx-4"
                        value={2}
                        disabled={hasVoted}
                        onChange={e=>this.rateHandler(e.target.value, row.id)}
                    >
                        <option value={5}>5</option>
                        <option value={4}>4</option>
                        <option value={3}>3</option>
                        <option value={2}>2</option>
                        <option value={1}>1</option>
                    </Input>
                )
            },
            {
                name: "Binary Download Link",
                selector: row => row['binary_URL'],
                reorder:true,
                grow: 3,
                // omit: row => { return row.binary_URL == null;},
                format: row => <a target="_blank" rel="noreferrer" href={row.binary_URL}>{removeHttp(row.binary_URL)}</a>
            }
        
        ];

        return (
            <div className="ps-5 pb-3">
                <DataTable
                    customStyles={versionsDataTableStyles}
                    theme="light"
                    data={[...this.state.data]}
                    columns={columns}
                    // defaultSortField="distro"
                    dense
                    highlightOnHover
                    responsive
                    selectableRows
                    selectableRowsSingle
                    selectableRowsNoSelectAll
                    selectableRowsHighlight
                    onSelectedRowsChange={this.selectedRowsChangedHandler}
                />
            </div>

        );
    }

    componentDidMount () {
        console.log("Package versions list did mount");
    }

    componentDidUpdate () {
        console.log("Package versions list did update");
        this.filterPackages();
    }


}

export default withRouter(VersionsList);