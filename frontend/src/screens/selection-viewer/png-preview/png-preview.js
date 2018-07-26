import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import PropTypes from 'prop-types';
import FormLabel from '@material-ui/core/FormLabel';

const apiUrl = process.env.REACT_APP_API;

const styles = {
  iframe: {
    height: 'calc(100vh - 135px)',
    width: '70vw',
  },
  preview: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  },
  button: {
    float: 'right',
  },
  spectrographLabel: {
    paddingBottom: 10,
  },
  main: {
    margin: '16px',
    padding: '16px',
  },
};

class PNGPreview extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      arm: null,
      spectrograph: [],
      processing: null,
    };
  }

  static propTypes = {
    arm: PropTypes.string,
    spectrograph: PropTypes.array,
    classes: PropTypes.object,
    processing: PropTypes.string,
    loadEnd: PropTypes.func.isRequired,
  };

  componentDidMount() {
    document.title = 'PNG Viewer';
    if (window.location.pathname === '/ccd-viewer') {
      if (
        window.location.search.includes('exposure=') &&
        window.location.search.includes('night=')
      ) {
        const str = window.location.search;
        const exposureId = str.substring(
          str.lastIndexOf('exposure='),
          str.lastIndexOf('&')
        );
        const night = str.substring(str.lastIndexOf('night='));
        this.setState({
          exposureId,
          night,
        });
      }
    }
  }

  renderImage = () => {
    const { classes } = this.props;
    let url = '';

    if (
      this.props.arm !== null &&
      this.props.processing !== null &&
      this.props.spectrograph.length !== 0
    )
      url = `${apiUrl}dashboard/fits_to_png/?process_id=1&cam=${
        this.props.arm
      }${this.props.spectrograph}&${this.state.night}&${
        this.state.exposureId
      }&processing=${this.props.processing}`;

    return (
      <iframe
        title="image-modal"
        className={classes.iframe}
        frameBorder="0"
        src={url}
        onLoad={this.props.loadEnd}
      />
    );
  };

  render() {
    const { classes } = this.props;
    return (
      <div className={classes.preview}>
        <FormLabel component="legend">Preview:</FormLabel>
        {this.renderImage()}
      </div>
    );
  }
}

export default withStyles(styles)(PNGPreview);
