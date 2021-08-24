'use strict';

const e = React.createElement;

class LikeButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = { liked: false };
  }

  render() {
    if (this.state.liked) {
      return 'You liked this.';
    }

    return e(
      'button',
      { onClick: () => this.setState({ liked: true }),
      'class': 'btn btn-primary'},
      'Like'
    );
  }
}

class Navigation extends React.Component {
    constructor(props) {
        super(props);
    }

    render () {
        return <nav className="navbar no-gutters g-pa-0">
            <div className="col-auto d-flex flex-nowrap u-header-logo-toggler g-py-12">
                <a href="../index.html" className="navbar-brand d-flex align-self-center g-hidden-xs-down g-line-height-1 py-0 g-mt-5">
                    <img src='/static/img/horizontal_on_corporate.jpeg' className="u-header-logo" />
                </a>

                <a className="js-side-nav u-header__nav-toggler d-flex align-self-center ml-auto" href="#"
                   data-hssm-class="u-side-nav--mini u-sidebar-navigation-v1--mini"
                   data-hssm-body-class="u-side-nav-mini" data-hssm-is-close-all-except-this="true"
                   data-hssm-target="#sideNav">
                    <i className="hs-admin-align-left"></i>
                </a>
            </div>

            <form id="searchMenu" class="u-header--search col-sm g-py-12 g-ml-15--sm g-ml-20--md g-mr-10--sm" aria-labelledby="searchInvoker" action="#!">
              <div class="input-group g-max-width-450--sm">
                  <input class="form-control h-100 form-control-md g-rounded-4 g-pr-40" type="text" placeholder="Enter search keywords"></input>
                <button type="submit" class="btn u-btn-outline-primary g-brd-none g-bg-transparent--hover g-pos-abs g-top-0 g-right-0 d-flex g-width-40 h-100 align-items-center justify-content-center g-font-size-18 g-z-index-2"><i class="hs-admin-search"></i>
                </button>
              </div>
            </form>

            <div class="col-auto d-flex g-py-12 g-pl-40--lg ml-auto">

              <div class="g-pos-rel g-hidden-sm-down g-mr-5">
                <a id="messagesInvoker" class="d-block text-uppercase u-header-icon-v1 g-pos-rel g-width-40 g-height-40 rounded-circle g-font-size-20" href="#" aria-controls="messagesMenu" aria-haspopup="true" aria-expanded="false" data-dropdown-event="click" data-dropdown-target="#messagesMenu"
                data-dropdown-type="css-animation" data-dropdown-duration="300" data-dropdown-animation-in="fadeIn" data-dropdown-animation-out="fadeOut">
                  <span class="u-badge-v1 g-top-7 g-right-7 g-width-18 g-height-18 g-bg-primary g-font-size-10 g-color-white rounded-circle p-0">7</span>
                  <i class="hs-admin-comment-alt g-absolute-centered"></i>
                </a>

                <div id="messagesMenu" class="g-absolute-centered--x g-width-340 g-max-width-400 g-mt-17 rounded" aria-labelledby="messagesInvoker">
                  <div class="media u-header-dropdown-bordered-v1 g-pa-20">
                    <h4 class="d-flex align-self-center text-uppercase g-font-size-default g-letter-spacing-0_5 g-mr-20 g-mb-0">3 new messages</h4>
                    <div class="media-body align-self-center text-right">
                      <a class="g-color-secondary" href="#">View All</a>
                    </div>
                  </div>

                  <ul class="p-0 mb-0">
                    <li class="media g-pos-rel u-header-dropdown-item-v1 g-pa-20">
                      <div class="d-flex g-mr-15">
                        <img class="g-width-40 g-height-40 rounded-circle" src="/static/assets/img-temp/100x100/img5.jpg" alt="Image Description" />
                      </div>

                      <div class="media-body">
                        <h5 class="g-font-size-16 g-font-weight-400 g-mb-5"><a href="#">Verna Swanson</a></h5>
                        <p class="g-mb-10">Not so many years businesses used to grunt at using</p>

                        <em class="d-flex align-self-center align-items-center g-font-style-normal g-color-lightblue-v2">
                <i class="hs-admin-time icon-clock g-mr-5"></i> <small>5 Min ago</small>
              </em>
                      </div>
                      <a class="u-link-v2" href="#">Read</a>
                    </li>

                    <li class="media g-pos-rel u-header-dropdown-item-v1 g-pa-20">
                      <div class="d-flex g-mr-15">
                        <img class="g-width-40 g-height-40 rounded-circle" src="/static/assets/img-temp/100x100/img6.jpg" alt="Image Description" />
                      </div>

                      <div class="media-body">
                        <h5 class="g-font-size-16 g-font-weight-400 g-mb-5"><a href="#">Eddie Hayes</a></h5>
                        <p class="g-mb-10">But today and influence of is growing right along illustration</p>

                        <em class="d-flex align-self-center align-items-center g-font-style-normal g-color-lightblue-v2">
                <i class="hs-admin-time icon-clock g-mr-5"></i> <small>22 Min ago</small>
              </em>
                      </div>
                      <a class="u-link-v2" href="#">Read</a>
                    </li>

                    <li class="media g-pos-rel u-header-dropdown-item-v1 g-pa-20">
                      <div class="d-flex g-mr-15">
                        <img class="g-width-40 g-height-40 rounded-circle" src="/static/assets/img-temp/100x100/img7.jpg" alt="Image Description" />
                      </div>

                      <div class="media-body">
                        <h5 class="g-font-size-16 g-font-weight-400 g-mb-5"><a href="#">Herbert Castro</a></h5>
                        <p class="g-mb-10">But today, the use and influence of illustrations is growing right along</p>

                        <em class="d-flex align-self-center align-items-center g-font-style-normal g-color-lightblue-v2">
                <i class="hs-admin-time icon-clock g-mr-5"></i> <small>15 Min ago</small>
              </em>
                      </div>
                      <a class="u-link-v2" href="#">Read</a>
                    </li>
                  </ul>
                </div>

              </div>



              <div class="g-pos-rel g-hidden-sm-down">
                <a id="notificationsInvoker" class="d-block text-uppercase u-header-icon-v1 g-pos-rel g-width-40 g-height-40 rounded-circle g-font-size-20" href="#" aria-controls="notificationsMenu" aria-haspopup="true" aria-expanded="false" data-dropdown-event="click"
                data-dropdown-target="#notificationsMenu" data-dropdown-type="css-animation" data-dropdown-duration="300" data-dropdown-animation-in="fadeIn" data-dropdown-animation-out="fadeOut">
                  <i class="hs-admin-bell g-absolute-centered"></i>
                </a>

                <div id="notificationsMenu" class="js-custom-scroll g-absolute-centered--x g-width-340 g-max-width-400 g-height-400 g-mt-17 rounded" aria-labelledby="notificationsInvoker">
                  <div class="media text-uppercase u-header-dropdown-bordered-v1 g-pa-20">
                    <h4 class="d-flex align-self-center g-font-size-default g-letter-spacing-0_5 g-mr-20 g-mb-0">Notifications</h4>
                  </div>

                  <ul class="p-0 mb-0">

                    <li class="media u-header-dropdown-item-v1 g-parent g-px-20 g-py-15">
                      <div class="d-flex align-self-center u-header-dropdown-icon-v1 g-pos-rel g-width-55 g-height-55 g-font-size-22 rounded-circle g-mr-15">
                        <i class="hs-admin-bookmark-alt g-absolute-centered"></i>
                      </div>

                      <div class="media-body align-self-center">
                        <p class="mb-0">A Pocket PC is a handheld computer features</p>
                      </div>

                      <a class="d-flex g-color-lightblue-v2 g-font-size-12 opacity-0 g-opacity-1--parent-hover g-transition--ease-in g-transition-0_2" href="#">
                        <i class="hs-admin-close"></i>
                      </a>
                    </li>


                    <li class="media u-header-dropdown-item-v1 g-parent g-px-20 g-py-15">
                      <div class="d-flex align-self-center u-header-dropdown-icon-v1 g-pos-rel g-width-55 g-height-55 g-font-size-22 rounded-circle g-mr-15">
                        <i class="hs-admin-blackboard g-absolute-centered"></i>
                      </div>

                      <div class="media-body align-self-center">
                        <p class="mb-0">The first is a non technical method which requires</p>
                      </div>

                      <a class="d-flex g-color-lightblue-v2 g-font-size-12 opacity-0 g-opacity-1--parent-hover g-transition--ease-in g-transition-0_2" href="#">
                        <i class="hs-admin-close"></i>
                      </a>
                    </li>


                    <li class="media u-header-dropdown-item-v1 g-parent g-px-20 g-py-15">
                      <div class="d-flex align-self-center u-header-dropdown-icon-v1 g-pos-rel g-width-55 g-height-55 g-font-size-22 rounded-circle g-mr-15">
                        <i class="hs-admin-calendar g-absolute-centered"></i>
                      </div>

                      <div class="media-body align-self-center">
                        <p class="mb-0">Stu Unger is of the biggest superstarsis</p>
                      </div>

                      <a class="d-flex g-color-lightblue-v2 g-font-size-12 opacity-0 g-opacity-1--parent-hover g-transition--ease-in g-transition-0_2" href="#">
                        <i class="hs-admin-close"></i>
                      </a>
                    </li>


                    <li class="media u-header-dropdown-item-v1 g-parent g-px-20 g-py-15">
                      <div class="d-flex align-self-center u-header-dropdown-icon-v1 g-pos-rel g-width-55 g-height-55 g-font-size-22 rounded-circle g-mr-15">
                        <i class="hs-admin-pie-chart g-absolute-centered"></i>
                      </div>

                      <div class="media-body align-self-center">
                        <p class="mb-0">Sony laptops are among the most well known laptops</p>
                      </div>

                      <a class="d-flex g-color-lightblue-v2 g-font-size-12 opacity-0 g-opacity-1--parent-hover g-transition--ease-in g-transition-0_2" href="#">
                        <i class="hs-admin-close"></i>
                      </a>
                    </li>


                    <li class="media u-header-dropdown-item-v1 g-parent g-px-20 g-py-15">
                      <div class="d-flex align-self-center u-header-dropdown-icon-v1 g-pos-rel g-width-55 g-height-55 g-font-size-22 rounded-circle g-mr-15">
                        <i class="hs-admin-bookmark-alt g-absolute-centered"></i>
                      </div>

                      <div class="media-body align-self-center">
                        <p class="mb-0">A Pocket PC is a handheld computer features</p>
                      </div>

                      <a class="d-flex g-color-lightblue-v2 g-font-size-12 opacity-0 g-opacity-1--parent-hover g-transition--ease-in g-transition-0_2" href="#">
                        <i class="hs-admin-close"></i>
                      </a>
                    </li>


                    <li class="media u-header-dropdown-item-v1 g-parent g-px-20 g-py-15">
                      <div class="d-flex align-self-center u-header-dropdown-icon-v1 g-pos-rel g-width-55 g-height-55 g-font-size-22 rounded-circle g-mr-15">
                        <i class="hs-admin-blackboard g-absolute-centered"></i>
                      </div>

                      <div class="media-body align-self-center">
                        <p class="mb-0">The first is a non technical method which requires</p>
                      </div>

                      <a class="d-flex g-color-lightblue-v2 g-font-size-12 opacity-0 g-opacity-1--parent-hover g-transition--ease-in g-transition-0_2" href="#">
                        <i class="hs-admin-close"></i>
                      </a>
                    </li>

                  </ul>
                </div>

              </div>


              <a id="searchInvoker" class="g-hidden-sm-up text-uppercase u-header-icon-v1 g-pos-rel g-width-40 g-height-40 rounded-circle g-font-size-20" href="#" aria-controls="searchMenu" aria-haspopup="true" aria-expanded="false" data-is-mobile-only="true" data-dropdown-event="click"
              data-dropdown-target="#searchMenu" data-dropdown-type="css-animation" data-dropdown-duration="300" data-dropdown-animation-in="fadeIn" data-dropdown-animation-out="fadeOut">
                <i class="hs-admin-search g-absolute-centered"></i>
              </a>


              <div class="col-auto d-flex g-pt-5 g-pt-0--sm g-pl-10 g-pl-20--sm">
                <div class="g-pos-rel g-px-10--lg">
                  <a id="profileMenuInvoker" class="d-block" href="#" aria-controls="profileMenu" aria-haspopup="true" aria-expanded="false" data-dropdown-event="click" data-dropdown-target="#profileMenu" data-dropdown-type="css-animation" data-dropdown-duration="300"
                  data-dropdown-animation-in="fadeIn" data-dropdown-animation-out="fadeOut">
                    <span class="g-pos-rel">
            <span class="u-badge-v2--xs u-badge--top-right g-hidden-sm-up g-bg-secondary g-mr-5"></span>
                    <img class="g-width-30 g-width-40--md g-height-30 g-height-40--md rounded-circle g-mr-10--sm" src="/static/assets/img-temp/130x130/img1.jpg" alt="Image description" />
                    </span>
                    <span class="g-pos-rel g-top-2">
            <span class="g-hidden-sm-down">Charlie Bailey</span>
                    <i class="hs-admin-angle-down g-pos-rel g-top-2 g-ml-10"></i>
                    </span>
                  </a>


                  <ul id="profileMenu" class="g-pos-abs g-left-0 g-width-100x--lg g-nowrap g-font-size-14 g-py-20 g-mt-17 rounded" aria-labelledby="profileMenuInvoker">
                    <li class="g-hidden-sm-up g-mb-10">
                      <a class="media g-py-5 g-px-20" href="#">
                        <span class="d-flex align-self-center g-pos-rel g-mr-12">
              <span class="u-badge-v1 g-top-minus-3 g-right-minus-3 g-width-18 g-height-18 g-bg-secondary g-font-size-10 g-color-white rounded-circle p-0">10</span>
                        <i class="hs-admin-comment-alt"></i>
                        </span>
                        <span class="media-body align-self-center">Unread Messages</span>
                      </a>
                    </li>
                    <li class="g-hidden-sm-up g-mb-10">
                      <a class="media g-py-5 g-px-20" href="#">
                        <span class="d-flex align-self-center g-mr-12">
              <i class="hs-admin-bell"></i>
            </span>
                        <span class="media-body align-self-center">Notifications</span>
                      </a>
                    </li>
                    <li class="g-mb-10">
                      <a class="media g-color-primary--hover g-py-5 g-px-20" href="#">
                        <span class="d-flex align-self-center g-mr-12">
              <i class="hs-admin-user"></i>
            </span>
                        <span class="media-body align-self-center">My Profile</span>
                      </a>
                    </li>
                    <li class="g-mb-10">
                      <a class="media g-color-primary--hover g-py-5 g-px-20" href="#">
                        <span class="d-flex align-self-center g-mr-12">
              <i class="hs-admin-rocket"></i>
            </span>
                        <span class="media-body align-self-center">Upgrade Plan</span>
                      </a>
                    </li>
                    <li class="g-mb-10">
                      <a class="media g-color-primary--hover g-py-5 g-px-20" href="#">
                        <span class="d-flex align-self-center g-mr-12">
              <i class="hs-admin-layout-grid-2"></i>
            </span>
                        <span class="media-body align-self-center">Latest Projects</span>
                      </a>
                    </li>
                    <li class="g-mb-10">
                      <a class="media g-color-primary--hover g-py-5 g-px-20" href="#">
                        <span class="d-flex align-self-center g-mr-12">
              <i class="hs-admin-headphone-alt"></i>
            </span>
                        <span class="media-body align-self-center">Get Support</span>
                      </a>
                    </li>
                    <li class="mb-0">
                      <a class="media g-color-primary--hover g-py-5 g-px-20" href="#">
                        <span class="d-flex align-self-center g-mr-12">
              <i class="hs-admin-shift-right"></i>
            </span>
                        <span class="media-body align-self-center">Sign Out</span>
                      </a>
                    </li>
                  </ul>

                </div>
              </div>

            </div>

            <a id="activityInvoker" class="text-uppercase u-header-icon-v1 g-pos-rel g-width-40 g-height-40 rounded-circle g-font-size-20" href="#" aria-controls="activityMenu" aria-haspopup="true" aria-expanded="false" data-dropdown-event="click" data-dropdown-target="#activityMenu"
            data-dropdown-type="css-animation" data-dropdown-animation-in="fadeInRight" data-dropdown-animation-out="fadeOutRight" data-dropdown-duration="300">
              <i class="hs-admin-align-right g-absolute-centered"></i>
            </a>

        </nav>;
    }
}

class Header extends React.Component {
    constructor(props) {
        super(props);
    }

    render () {
        return <header id="js-header" className="u-header u-header--sticky-top">
                <div className="u-header__section u-header__section--admin-light g-min-height-65">
                    <Navigation></Navigation>
                </div>
            </header>
        ;
    }
}

class SideBarMenuItem extends React.Component {
    constructor(props) {
        super(props);
    }

    render () {
        return <li className="u-sidebar-navigation-v1-menu-item u-side-nav--top-level-menu-item">
            <a className="media u-side-nav--top-level-menu-link u-side-nav--hide-on-hidden g-px-15 g-py-12" href="../packages.html">
              <span className="d-flex align-self-center g-font-size-18 g-mr-18">
                    <i className="hs-admin-medall"></i>
              </span>
              <span className="media-body align-self-center">{this.props.title}</span>
            </a>
        </li>
    }
}

class SidebarNav extends React.Component {
    constructor() {
        super();
    }

    render () {
        return <div id="sideNav" className="col-auto u-sidebar-navigation-v1 u-sidebar-navigation--dark">
            <ul id="sideNavMenu" className="u-sidebar-navigation-v1-menu u-side-nav--top-level-menu g-min-height-100vh mb-0">
                <SideBarMenuItem title="1243" />
                <SideBarMenuItem title="1243" />
            </ul>
        </div>
    }
}

class DashBoard extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div className="col g-ml-45 g-ml-0--lg g-pb-65--md">
                <div className="g-pa-20">
                    123
                </div>
            </div>
        );
    }

}

class Main extends React.Component {
    constructor(props) {
        super(props);

    }

    render (){
        return <main className="container-fluid px-0 g-pt-65">
            <div className="row no-gutters g-pos-rel g-overflow-x-hidden">
                <SidebarNav></SidebarNav>
                <DashBoard></DashBoard>
            </div>
        </main>
    }

}

class WebApp extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <div>
            <Header></Header>
            <Main></Main>
        </div>;
    }

}

ReactDOM.render(e(WebApp), document.getElementById('root'));

console.log('main.js connected')