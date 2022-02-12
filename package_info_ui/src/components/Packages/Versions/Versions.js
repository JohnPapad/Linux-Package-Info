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
import jwt_decode from "jwt-decode";


class Versions extends Component {

    state = {
        versions: this.props.packageInfo.versions
    };

    skipRowsChangedTriggering = true;

    rateHandler = async (rate, versionIndexStr, packageVersionId, userId, userRating) => {
        const payload = {
            rate: Number(rate),
            pkg_version: packageVersionId,
            user: userId
        };

        let response = null;
        if (userRating) {
            // change existing rating
            response = await API.changePackageVersionRating(payload, userRating.rating_id);
        }
        else {
            // new rating
            response = await API.ratePackageVersion(payload);
        }

        if (!response) return;
        const versionIndex = Number(versionIndexStr);
        this.setState(
            produce(draft=>{
                draft.versions[versionIndex]["user_rating"] = {
                    "rate": response.data.rate,
                    "rating_id": response.data.id
                };
            })
        );
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
        let userId = null;
        try {
            userId = jwt_decode(localStorage.getItem("access_token"))['user_id'];
        }
        catch {}

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
                name: "Average Rating",
                selector: row => row['rating'],
                sortable: true,
                reorder:true,
                grow: 0.5,
                center: true,
                cell: row=>row.rating ? row.rating.toFixed(1) : "-"
            },
            {
                name: "Personal Rating",
                reorder:true,
                omit: !userId,
                grow: 0.5,
                center: true,
                cell: (row, index) =>(
                    <Input
                        type="select"
                        bsSize="sm"
                        className="my-1 mx-4"
                        value={row.user_rating ? row.user_rating.rate : 0}
                        onChange={e=>this.rateHandler(e.target.value, index, row.id, userId, row.user_rating)}
                    >
                        <option value={5}>5</option>
                        <option value={4}>4</option>
                        <option value={3}>3</option>
                        <option value={2}>2</option>
                        <option value={1}>1</option>
                        {
                            !row.user_rating &&
                            <option value={0}>-</option>
                        }
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
                    data={this.state.versions}
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

    componentWillUpdate () {
        this.skipRowsChangedTriggering = true;
    }

    componentDidUpdate () {
        console.log(`--> Versions [${this.props.packageInfo.name}]  did update`);
    }

    shouldComponentUpdate (nextProps, nextState) {
        return !isEqual(this.state.versions, nextState.versions);
    }
}

export default withRouter(Versions);