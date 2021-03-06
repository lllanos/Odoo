# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch

from odoo.addons.test_mail.tests.common import BaseFunctionalTest, MockEmails, TestRecipients
from odoo.tools import mute_logger
from odoo.tests import tagged


@tagged("odoobot")
class TestOdoobot(BaseFunctionalTest, MockEmails, TestRecipients):

    def setUp(self):
        super(TestOdoobot, self).setUp()
        self.odoobot = self.env.ref("mail_bot.partner_odoobot")
        self.message_post_default_kwargs = {
            'body': '',
            'attachment_ids': [],
            'message_type': 'comment',
            'partner_ids': [],
            'subtype': 'mail.mt_comment'
        }
        self.odoobot_ping_body = '<a href="http://odoo.com/web#model=res.partner&amp;id=%s" class="o_mail_redirect" data-oe-id="%s" data-oe-model="res.partner" target="_blank">@OdooBot</a>' % (self.odoobot.id, self.odoobot.id)
        self.test_record_employe = self.test_record.sudo(self.user_employee)

    @mute_logger('odoo.addons.mail.models.mail_mail')
    def test_odoobot_ping(self):
        kwargs = self.message_post_default_kwargs.copy()
        kwargs.update({'body': self.odoobot_ping_body, 'partner_ids': [self.odoobot.id, self.user_admin.partner_id.id]})

        with patch('random.choice', lambda x: x[0]):
            self.assertNextMessage(
                self.test_record_employe.with_context({'mail_post_autofollow': True}).message_post(**kwargs),
                sender=self.odoobot,
                answer=["Yaaaay that's me!"]  # no the perfect idea to base a test on a random but it should work for test phase, better mock random choice?
            )
        # Odoobot should not be a follower but user_employee and user_admin should
        follower = self.test_record.message_follower_ids.mapped('partner_id')
        self.assertNotIn(self.odoobot, follower)
        self.assertIn(self.user_employee.partner_id, follower)
        self.assertIn(self.user_admin.partner_id, follower)

    @mute_logger('odoo.addons.mail.models.mail_mail')
    def test_onboarding_flow(self):
        kwargs = self.message_post_default_kwargs.copy()
        channel = self.env['mail.channel'].sudo(self.user_employee).init_odoobot()

        kwargs['body'] = 'tagada 😊'
        self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.odoobot,
            answer="Great! :) Did you notice that you can also send attachments, like a picture of your cute dog? Try it!"
        )
        kwargs['body'] = ''
        kwargs['attachment_ids'] = [1]
        last_message = self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.odoobot,
            answer="Not a cute dog, but you get it :) To access special features, start your sentence with '/' (e.g. /help)."
        )
        kwargs['attachment_ids'] = []

        channel.execute_command(command="help")
        self.assertNextMessage(
            last_message,  # no message will be post with command help, use last odoobot message instead
            sender=self.odoobot,
            answer="Wow you are a natural! Ping someone to grab its attention with @nameoftheuser. Try to ping me with <b>@OdooBot</b>."
        )
        # we dont test the end of the flow since it will depends of the installed apps (livechat)

        kwargs['partner_ids'] = []
        kwargs['body'] = "I love you"
        self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.odoobot,
            answer="Aaaaaw that's really cute but, you know, bots don't work that way. You're too human for me! Let's keep it professional ❤️"
        )
        kwargs['body'] = "Go fuck yourself"
        self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.odoobot,
            answer="That's not a really nice thing to say, you know? I'm a bot but I have feelings, ok?! 💔"
        )
        # we should have a default answer
        with patch('random.choice', lambda x: x[0]):
            kwargs['body'] = "I'm batman"
            self.assertNextMessage(
                channel.message_post(**kwargs),
                sender=self.odoobot,
                answer="Mmmmh I'm not sure what you mean.. Can you try again?"
            )

    @mute_logger('odoo.addons.mail.models.mail_mail')
    def test_odoobot_no_default_answer(self):
        kwargs = self.message_post_default_kwargs.copy()
        kwargs.update({'body': "I'm not talking to @odoobot right now", 'partner_ids': []})
        self.assertNextMessage(
            self.test_record_employe.message_post(**kwargs),
            answer=False
        )

    def assertNextMessage(self, message, answer=None, sender=None):
        last_message = self.env['mail.message'].search([('id', '=', message.id + 1)])
        if last_message:
            body = last_message.body.replace('<p>', '').replace('</p>', '')
        else:
            self.assertFalse(answer, "No last message found when an answer was expect")
        if answer is not None:
            if answer and not last_message:
                self.assertTrue(False, "No last message found")
            if isinstance(answer, list):
                self.assertIn(body, answer)
            elif isinstance(answer, tuple):
                for elem in answer:
                    self.assertIn(elem, body)
            elif not answer:
                self.assertFalse(last_message, "No answer should have been post")
                return
            else:
                self.assertEqual(body, answer)
        if sender:
            self.assertEqual(sender, last_message.author_id)
        return last_message
