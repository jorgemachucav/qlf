import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Badge from '@material-ui/core/Badge';
import Icon from '@material-ui/core/Icon';
import Popover from '@material-ui/core/Popover';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';
import Button from '@material-ui/core/Button';
import { connect } from 'react-redux';
import moment from 'moment';
import {
  clearNotifications,
  setSound,
} from '../../containers/online/online-store';

const styles = {
  container: {
    cursor: 'pointer',
  },
  margin: {
    margin: 1,
  },
  padding: {
    padding: 2,
  },
  notificationsIcon: {
    fontSize: 20,
    alignSelf: 'center',
    paddingRight: '8px',
    cursor: 'pointer',
  },
  badge: {
    height: 16,
    width: 16,
    top: -5,
    right: 0,
  },
  alert: {
    color: 'rgb(255, 61, 0)',
  },
  warning: {
    color: '#FF6F00',
  },
  listStyle: {
    padding: 0,
    maxHeight: 300,
    overflowY: 'auto',
  },
  none: {
    display: 'none',
  },
  volumeIcon: {
    fontSize: 20,
    alignSelf: 'center',
    paddingRight: '8px',
    cursor: 'pointer',
    verticalAlign: 'middle',
  },
};

class Notification extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      anchorEl: null,
      errors: [],
      warnings: [],
    };
  }

  static propTypes = {
    notifications: PropTypes.array.isRequired,
    clearNotifications: PropTypes.func.isRequired,
    classes: PropTypes.object.isRequired,
    soundActivated: PropTypes.bool.isRequired,
    setSound: PropTypes.func.isRequired,
  };

  handleNotificationClick = event => {
    this.setState({
      anchorEl: event.currentTarget,
    });
  };

  handlePopOverClose = () => {
    this.setState({
      anchorEl: null,
    });
  };

  clear = () => {
    this.props.clearNotifications();
    this.setState({ anchorEl: null });
  };

  renderNotifications = () => {
    const { classes } = this.props;
    const count = this.props.notifications.length;
    if (!count) return;
    return (
      <div>
        <List style={styles.listStyle}>
          {this.props.notifications.map((notif, id) => {
            const stylePrimary =
              notif.type === 'ALARM' ? classes.alert : classes.warning;
            const date = moment(new Date(notif.date)).fromNow();
            return (
              <div key={id}>
                <ListItem>
                  <ListItemText
                    primary={notif.text}
                    secondary={date}
                    classes={{
                      primary: stylePrimary,
                      secondary: classes.secondary,
                    }}
                  />
                </ListItem>
                <Divider />
              </div>
            );
          })}
        </List>
        <Button onClick={this.clear} className={classes.button}>
          Clear
        </Button>
      </div>
    );
  };

  onToggleSound = () => {
    this.props.setSound(!this.props.soundActivated);
  };

  render() {
    const { classes } = this.props;
    const count = this.props.notifications.length;
    const badge = count ? classes.badge : classes.none;
    return (
      <div style={styles.container}>
        <Icon onClick={this.onToggleSound} style={styles.volumeIcon}>
          {this.props.soundActivated ? 'volume_up' : 'volume_off'}
        </Icon>
        <Popover
          open={Boolean(this.state.anchorEl)}
          anchorEl={this.state.anchorEl}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          onClose={this.handlePopOverClose}
          elevation={1}
        >
          {this.renderNotifications()}
        </Popover>
        <Badge
          className={classes.margin}
          badgeContent={count}
          classes={{
            root: classes.root,
            badge: badge,
          }}
          onClick={this.handleNotificationClick}
          color="error"
        >
          <Icon style={styles.notificationsIcon}>notifications</Icon>
        </Badge>
      </div>
    );
  }
}

const NotificationWithStyles = withStyles(styles)(Notification);

export default connect(
  state => ({
    notifications: state.qlfOnline.notifications,
    soundActivated: state.qlfOnline.soundActivated,
  }),
  dispatch => ({
    clearNotifications: () => dispatch(clearNotifications()),
    setSound: soundActivated => dispatch(setSound(soundActivated)),
  })
)(NotificationWithStyles);
