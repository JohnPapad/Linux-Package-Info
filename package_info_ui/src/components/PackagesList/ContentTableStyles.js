import { createTheme } from 'react-data-table-component';

const dividerColor = "rgba(0,0,0,.12)";

export const versionsDataTableStyles = {
    table: {
		style: {
            borderBottom: `1px solid ${dividerColor}`,
		},
	},
    headCells: {
        style: {
            borderLeft: `1px solid ${dividerColor}`,
        },
    },
    cells: {
        style: {
            borderLeft: `1px solid ${dividerColor}`,
        },
    }
};

export const packagesDataTableStyles = {
    table: {
		style: {
            border: `1px solid ${dividerColor}`,
		},
	},
    headRow: {
        style: {
            fontSize: "120%"
        },
    },
    expanderRow: {
		style: {
            borderBottom: `1px solid ${dividerColor}`,
		},
	},
    expanderButton: {
		style: {
			'&:focus': {
                backgroundColor: "#f8f9fa",
			},
		}
    }
};

createTheme('light', {
    background: {
      default: '#f8f9fa',
    },
});