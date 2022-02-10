import { Component } from "react";
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


class Versions extends Component {

    skipRowsChangedTriggering = true;

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

    selectedRowsChangedHandler = state => {
        if (this.skipRowsChangedTriggering) {
            this.skipRowsChangedTriggering = false;
            return;
        }
        console.log("selected versions: ", state, "selectedVersion: ", this.props.selectedVersion)
        if (state.selectedCount === 0) {
            this.props.packageVersionSelectedHandler(this.props.packageInfo);
        }
        else {
            const currSelectedVersion = state.selectedRows[0].version;
            this.props.packageVersionSelectedHandler(this.props.packageInfo, currSelectedVersion);
        }
    }

    versionIsSelected = row => {
        return row.version === this.props.selectedVersion;
    }

    render() {
        const isAuth = true;
        const hasVoted = false;

        console.log(`--> Versions [${this.props.packageInfo.name}] rendered`)
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
                format: row => <a target="_blank" rel="noreferrer" href={row.binary_URL}>{removeHttp(row.binary_URL)}</a>
            }
        
        ];

        return (
            <div className="ps-5 pb-3">
                <DataTable
                    customStyles={versionsDataTableStyles}
                    theme="light"
                    data={this.props.packageInfo.versions}
                    columns={columns}
                    dense
                    highlightOnHover
                    responsive
                    selectableRows
                    selectableRowsSingle
                    selectableRowsNoSelectAll
                    selectableRowSelected={this.versionIsSelected}
                    onSelectedRowsChange={this.selectedRowsChangedHandler}
                />
            </div>

        );
    }

    componentDidMount () {
        console.log(`--> Versions [${this.props.packageInfo.name}] did mount`);
    }

    componentDidUpdate () {
        console.log(`--> Versions [${this.props.packageInfo.name}]  did update`);
    }

    shouldComponentUpdate (nextProps, nextState) {
        return nextProps.selectedVersion != this.props.selectedVersion;
    }
}

export default withRouter(Versions);