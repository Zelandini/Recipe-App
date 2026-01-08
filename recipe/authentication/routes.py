# recipe/authentication/routes.py
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from recipe.domainmodel.user import User


from password_validator import PasswordValidator
import recipe.authentication.services as services

authentication_blueprint = Blueprint("authentication_bp", __name__, template_folder="../templates")


class PasswordValid:
    def __init__(self, message=None):
        if not message:
            message = 'Your password must be at least 8 characters, and contain an upper case letter, a lower case letter and a digit'
        self.message = message

    def __call__(self, form, field):
        schema = PasswordValidator()
        schema \
            .min(8) \
             .has().uppercase() \
            .has().lowercase() \
            .has().digits()
        if not schema.validate(field.data):
            raise ValidationError(self.message)


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(message='Your username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    password = PasswordField("Password", validators=[
        DataRequired(message='Your password is required'),
        PasswordValid()
    ])
    confirm = PasswordField("Confirm Password", validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo("password", message='Passwords must match')
    ])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(message='Username is required')])
    password = PasswordField("Password", validators=[DataRequired(message='Password is required')])
    submit = SubmitField("Login")


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("authentication_bp.login", next=request.url))
        return view(*args, **kwargs)

    return wrapped_view


@authentication_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    user_name_not_unique = None

    if form.validate_on_submit():
        # Successful POST, i.e. the username and password have passed validation checking.
        # Use the service layer to attempt to add the new user.
        try:
            services.add_user(form.username.data, form.password.data, current_app.repository)
            # All is well, redirect the user to the login page.
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("authentication_bp.login"))

        except services.NameNotUniqueException:
            user_name_not_unique = 'Your user name is already taken - please supply another'

    # For a GET or a failed POST request, return the Registration Web page.
    return render_template(
        "authentication/credentials.html",
        form=form,
        form_type="register",
        user_name_error_message=user_name_not_unique
    )


@authentication_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    user_name_not_recognised = None
    password_does_not_match_user_name = None

    if form.validate_on_submit():
        # Successful POST, i.e. the username and password have passed validation checking.
        # Use the service layer to lookup the user.
        try:
            user = services.get_user(form.username.data, current_app.repository)

            # Authenticate user.
            authenticated_user = services.authenticate_user(
                user['username'], form.password.data, current_app.repository
            )

            # Initialize session and redirect the user to the home page.
            session.clear()
            session["username"] = authenticated_user.username
            session["user_id"] = authenticated_user.id
            flash("Logged in successfully.", "success")

            # Redirect to the 'next' page or home page
            next_url = request.args.get("next") or url_for("home.index")
            return redirect(next_url)

        except services.UnknownUserException:
            # User name not known to the system, set a suitable error message.
            user_name_not_recognised = 'User name not recognised - please supply another'

        except services.AuthenticationException:
            # Authentication failed, set a suitable error message.
            password_does_not_match_user_name = 'Password does not match supplied user name - please check and try again'

    # For a GET or a failed POST, return the Login Web page.
    return render_template(
        "authentication/credentials.html",
        form=form,
        form_type="login",
        user_name_error_message=user_name_not_recognised,
        password_error_message=password_does_not_match_user_name
    )


@authentication_blueprint.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("home.index"))


# Replace your debug route with this more comprehensive version
@authentication_blueprint.route('/debug')
def debug_users():
    """Comprehensive debug route"""
    debug_info = []

    try:
        # Import User class - adjust this path to match your project structure
        from recipe.domainmodel.user import User  # or wherever your User class is
        from werkzeug.security import generate_password_hash

        repo = current_app.repository
        debug_info.append(f"Repository type: {type(repo)}")
        debug_info.append("=" * 50)

        # Test both user methods
        test_usernames = ["test", "admin", "demo", "testuser"]
        for test_username in test_usernames:
            try:
                user1 = repo.get_user(test_username)
                user2 = repo.get_user_by_username(test_username)
                debug_info.append(f"Testing username: '{test_username}'")
                debug_info.append(f"  get_user('{test_username}'): {user1}")
                debug_info.append(f"  get_user_by_username('{test_username}'): {user2}")
                debug_info.append("")
            except Exception as e:
                debug_info.append(f"Error with '{test_username}': {str(e)}")

        debug_info.append("=" * 50)

        # Check what next_user_id returns
        try:
            next_id = repo.next_user_id()
            debug_info.append(f"next_user_id(): {next_id}")
            debug_info.append(f"This suggests {next_id - 1} users have been added")
        except Exception as e:
            debug_info.append(f"next_user_id() error: {str(e)}")

        debug_info.append("=" * 50)

        # Let's try to create a test user right now
        try:
            test_user = User("debugtest", generate_password_hash("password123"))
            debug_info.append(f"Created test user: {test_user}")
            debug_info.append(f"User ID before adding: {test_user.id}")

            # Try adding the user
            repo.add_user(test_user)
            debug_info.append(f"User ID after adding: {test_user.id}")
            debug_info.append("Successfully added test user")

            # Try retrieving it immediately
            retrieved = repo.get_user_by_username("debugtest")
            debug_info.append(f"Retrieved user: {retrieved}")

        except Exception as e:
            debug_info.append(f"Error creating/adding test user: {str(e)}")
            import traceback
            debug_info.append(f"Traceback: {traceback.format_exc()}")

    except Exception as e:
        debug_info.append(f"Major error: {str(e)}")
        import traceback
        debug_info.append(f"Traceback: {traceback.format_exc()}")

    return "<pre>" + "\n".join(debug_info) + "</pre>"


@authentication_blueprint.route('/test-registration')
def test_registration():
    """Test the registration process manually"""
    debug_info = []

    try:
        # Import with correct path
        from recipe.domainmodel.user import User
        from werkzeug.security import generate_password_hash
        import recipe.authentication.services as services

        username = "manualtest"
        password = "password123"

        debug_info.append(f"Testing registration for: {username}")

        # Step 1: Check if user already exists
        try:
            existing = current_app.repository.get_user_by_username(username)
            debug_info.append(f"User already exists: {existing}")
            if existing:
                debug_info.append("User already exists, skipping registration")
                return "<pre>" + "\n".join(debug_info) + "</pre>"
        except Exception as e:
            debug_info.append(f"Checking existing user: {str(e)}")

        # Step 2: Try to add user using services
        try:
            services.add_user(username, password, current_app.repository)
            debug_info.append("✓ User added successfully via services")
        except Exception as e:
            debug_info.append(f"✗ Failed to add user via services: {str(e)}")
            import traceback
            debug_info.append(f"Traceback: {traceback.format_exc()}")
            return "<pre>" + "\n".join(debug_info) + "</pre>"

        # Step 3: Try to retrieve the user
        try:
            user = current_app.repository.get_user_by_username(username)
            debug_info.append(f"✓ Retrieved user: {user}")
            debug_info.append(f"  Username: {user.username}")
            debug_info.append(f"  ID: {user.id}")
        except Exception as e:
            debug_info.append(f"✗ Failed to retrieve user: {str(e)}")

        # Step 4: Try authentication
        try:
            auth_user = services.authenticate_user(username, password, current_app.repository)
            auth_user = services.authenticate_user(username, password, current_app.repository)
            debug_info.append(f"✓ Authentication successful: {auth_user}")
        except Exception as e:
            debug_info.append(f"✗ Authentication failed: {str(e)}")

    except Exception as e:
        debug_info.append(f"Major error: {str(e)}")
        import traceback
        debug_info.append(f"Traceback: {traceback.format_exc()}")

    return "<pre>" + "\n".join(debug_info) + "</pre>"