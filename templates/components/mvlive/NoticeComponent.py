from flask import current_app

from LiveComponent import LiveComponent
#from packages.Hubi import render


class NoticeComponent(LiveComponent):

    def mount(self):
        self.notice: None
        self.subject: str = ""
        print("Notice Mounted")

    def updatedNotice(self):
        if "iframe" not in self.notice:
            self.notice = ""
        if "office.com" not in self.notice and "google.com" not in self.notice and "youtube.com" not in self.notice:
            print("guvk")
            self.notice = ""
        if "iframe" in self.notice:
            self.notice = self.notice[:7] + " class='w-100' " + self.notice[7:]

    def publish_notice(self):
        # Notice.create({})
        print("Publishing Notice")

    def render(self):
        # language=HTML
        return """
        <!--html-->
            <div class='row'>
                <div class='col-lg-4'>
                    <div class="form-group">
              <label for="">Notice Subject</label>
              <input type="text"
                class="form-control" data-model='debounce(350ms)|subject' name="" id="" aria-describedby="helpId" placeholder="">
              <small id="helpId" class="form-text text-muted">Users will see this as the description of this notice.</small>
            </div>
            <br>
            <div class="form-group">
                <label for=''>Paste Embedded Document Here. </label>
              <textarea data-model='debounce(350ms)|notice' class="form-control" name="notice" id="" rows="12"></textarea>
              <small id="helpId" class="form-text text-muted">Supports embedded documents from Microsoft Word / Google Docs</small>
            </div>
            <br>
            <br>
            <br>
                </div>
                
                <div class='col-lg-8'>
            <p class='text-right mb-2'>
                {% if notice %}
                    <button data-action='publish_notice' class="btn btn-primary float-right ">Publish Notice</button>
                {% endif %}
            </p>
            <p>
                <span class='border-bottom'>
                    Preview Area
                </span>
            </p>

                <div id='preview-area'>
                    <h5>{{ subject }}</h5>
                    <p class='text-center'>
                        {{ notice|safe }}
                    </p>
                </div>
                
                
                

                    </div>
            </div>
        <!--!html-->
        """
