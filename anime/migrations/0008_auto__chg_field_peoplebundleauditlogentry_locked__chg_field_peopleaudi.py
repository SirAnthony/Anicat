# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'PeopleBundleAuditLogEntry.locked'
        db.alter_column(u'anime_peoplebundleauditlogentry', 'locked', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'PeopleAuditLogEntry.locked'
        db.alter_column(u'anime_peopleauditlogentry', 'locked', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'AnimeLinkAuditLogEntry.locked'
        db.alter_column(u'anime_animelinkauditlogentry', 'locked', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'AnimeItemAuditLogEntry.locked'
        db.alter_column(u'anime_animeitemauditlogentry', 'locked', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'AnimeNameAuditLogEntry.locked'
        db.alter_column(u'anime_animenameauditlogentry', 'locked', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'AnimeEpisodeAuditLogEntry.locked'
        db.alter_column(u'anime_animeepisodeauditlogentry', 'locked', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'OrganisationAuditLogEntry.locked'
        db.alter_column(u'anime_organisationauditlogentry', 'locked', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'OrganisationBundleAuditLogEntry.locked'
        db.alter_column(u'anime_organisationbundleauditlogentry', 'locked', self.gf('django.db.models.fields.NullBooleanField')(null=True))

    def backwards(self, orm):

        # Changing field 'PeopleBundleAuditLogEntry.locked'
        db.alter_column(u'anime_peoplebundleauditlogentry', 'locked', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'PeopleAuditLogEntry.locked'
        db.alter_column(u'anime_peopleauditlogentry', 'locked', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'AnimeLinkAuditLogEntry.locked'
        db.alter_column(u'anime_animelinkauditlogentry', 'locked', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'AnimeItemAuditLogEntry.locked'
        db.alter_column(u'anime_animeitemauditlogentry', 'locked', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'AnimeNameAuditLogEntry.locked'
        db.alter_column(u'anime_animenameauditlogentry', 'locked', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'AnimeEpisodeAuditLogEntry.locked'
        db.alter_column(u'anime_animeepisodeauditlogentry', 'locked', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'OrganisationAuditLogEntry.locked'
        db.alter_column(u'anime_organisationauditlogentry', 'locked', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'OrganisationBundleAuditLogEntry.locked'
        db.alter_column(u'anime_organisationbundleauditlogentry', 'locked', self.gf('django.db.models.fields.BooleanField')())

    models = {
        u'anime.animebundle': {
            'Meta': {'object_name': 'AnimeBundle'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'anime.animeepisode': {
            'Meta': {'unique_together': "(('title', 'anime'),)", 'object_name': 'AnimeEpisode'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'animeepisodes'", 'to': u"orm['anime.AnimeItem']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'anime.animeepisodeauditlogentry': {
            'Meta': {'ordering': "('-action_date', 'action_id')", 'object_name': 'AnimeEpisodeAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_ip': ('audit_log.models.fields.LastIPField', [], {'max_length': '15'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_animeepisode_audit_log_entry'"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_animeepisodes'", 'to': u"orm['anime.AnimeItem']"}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'anime.animeitem': {
            'Meta': {'ordering': "['title']", 'object_name': 'AnimeItem'},
            'air': ('django.db.models.fields.BooleanField', [], {}),
            'bundle': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'animeitems'", 'null': 'True', 'to': u"orm['anime.AnimeBundle']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'endedAt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'endedKnown': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'episodesCount': ('django.db.models.fields.IntegerField', [], {}),
            'genre': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['anime.Genre']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'releaseType': ('django.db.models.fields.IntegerField', [], {}),
            'releasedAt': ('django.db.models.fields.DateTimeField', [], {}),
            'releasedKnown': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'anime.animeitemauditlogentry': {
            'Meta': {'ordering': "('-action_date', 'action_id')", 'object_name': 'AnimeItemAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_ip': ('audit_log.models.fields.LastIPField', [], {'max_length': '15'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_animeitem_audit_log_entry'"}),
            'air': ('django.db.models.fields.BooleanField', [], {}),
            'bundle': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_auditlog_animeitems'", 'null': 'True', 'to': u"orm['anime.AnimeBundle']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'endedAt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'endedKnown': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'episodesCount': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'releaseType': ('django.db.models.fields.IntegerField', [], {}),
            'releasedAt': ('django.db.models.fields.DateTimeField', [], {}),
            'releasedKnown': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'anime.animelink': {
            'Meta': {'unique_together': "(('link', 'anime'),)", 'object_name': 'AnimeLink'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': u"orm['anime.AnimeItem']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '250'}),
            'linkType': ('django.db.models.fields.IntegerField', [], {})
        },
        u'anime.animelinkauditlogentry': {
            'Meta': {'ordering': "('-action_date', 'action_id')", 'object_name': 'AnimeLinkAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_ip': ('audit_log.models.fields.LastIPField', [], {'max_length': '15'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_animelink_audit_log_entry'"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_links'", 'to': u"orm['anime.AnimeItem']"}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '250'}),
            'linkType': ('django.db.models.fields.IntegerField', [], {}),
            'locked': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        u'anime.animename': {
            'Meta': {'ordering': "['title']", 'unique_together': "(('title', 'anime'),)", 'object_name': 'AnimeName'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'animenames'", 'to': u"orm['anime.AnimeItem']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'anime.animenameauditlogentry': {
            'Meta': {'ordering': "('-action_date', 'action_id')", 'object_name': 'AnimeNameAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_ip': ('audit_log.models.fields.LastIPField', [], {'max_length': '15'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_animename_audit_log_entry'"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_animenames'", 'to': u"orm['anime.AnimeItem']"}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'anime.animerequest': {
            'Meta': {'object_name': 'AnimeRequest'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'requests'", 'null': 'True', 'to': u"orm['anime.AnimeItem']"}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'requestType': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'anime.credit': {
            'Meta': {'object_name': 'Credit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'anime.genre': {
            'Meta': {'ordering': "['name']", 'object_name': 'Genre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        },
        u'anime.organisation': {
            'Meta': {'object_name': 'Organisation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'anime.organisationauditlogentry': {
            'Meta': {'ordering': "('-action_date', 'action_id')", 'object_name': 'OrganisationAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_ip': ('audit_log.models.fields.LastIPField', [], {'max_length': '15'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_organisation_audit_log_entry'"}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'anime.organisationbundle': {
            'Meta': {'unique_together': "(('anime', 'organisation', 'job', 'role'),)", 'object_name': 'OrganisationBundle'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organisationbundles'", 'to': u"orm['anime.AnimeItem']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['anime.Credit']"}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organisationbundles'", 'to': u"orm['anime.Organisation']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        u'anime.organisationbundleauditlogentry': {
            'Meta': {'ordering': "('-action_date', 'action_id')", 'object_name': 'OrganisationBundleAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_ip': ('audit_log.models.fields.LastIPField', [], {'max_length': '15'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_organisationbundle_audit_log_entry'"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_organisationbundles'", 'to': u"orm['anime.AnimeItem']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['anime.Credit']"}),
            'locked': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_organisationbundles'", 'to': u"orm['anime.Organisation']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        u'anime.people': {
            'Meta': {'object_name': 'People'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'anime.peopleauditlogentry': {
            'Meta': {'ordering': "('-action_date', 'action_id')", 'object_name': 'PeopleAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_ip': ('audit_log.models.fields.LastIPField', [], {'max_length': '15'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_people_audit_log_entry'"}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'anime.peoplebundle': {
            'Meta': {'unique_together': "(('anime', 'person', 'job', 'role'),)", 'object_name': 'PeopleBundle'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'peoplebundles'", 'to': u"orm['anime.AnimeItem']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['anime.Credit']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'peoplebundles'", 'to': u"orm['anime.People']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        u'anime.peoplebundleauditlogentry': {
            'Meta': {'ordering': "('-action_date', 'action_id')", 'object_name': 'PeopleBundleAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_ip': ('audit_log.models.fields.LastIPField', [], {'max_length': '15'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_peoplebundle_audit_log_entry'"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_peoplebundles'", 'to': u"orm['anime.AnimeItem']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['anime.Credit']"}),
            'locked': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_peoplebundles'", 'to': u"orm['anime.People']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        u'anime.userstatusbundle': {
            'Meta': {'unique_together': "(('anime', 'user'),)", 'object_name': 'UserStatusBundle'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'statusbundles'", 'to': u"orm['anime.AnimeItem']"}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '6', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['anime']