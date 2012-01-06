# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'AnimeLinksAuditLogEntry'
        db.delete_table('anime_animelinksauditlogentry')

        # Deleting model 'AnimeLinks'
        db.delete_table('anime_animelinks')


    def backwards(self, orm):
        
        # Adding model 'AnimeLinksAuditLogEntry'
        db.create_table('anime_animelinksauditlogentry', (
            ('action_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_animelinks_audit_log_entry', null=True, to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.IntegerField')(blank=True, db_index=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ANN', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('AniDB', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_links1', to=orm['anime.AnimeItem'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('MAL', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True, db_index=True)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('anime', ['AnimeLinksAuditLogEntry'])

        # Adding model 'AnimeLinks'
        db.create_table('anime_animelinks', (
            ('ANN', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('AniDB', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('MAL', self.gf('django.db.models.fields.IntegerField')(unique=True, null=True, blank=True)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='links1', to=orm['anime.AnimeItem'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('anime', ['AnimeLinks'])


    models = {
        'anime.animebundle': {
            'Meta': {'object_name': 'AnimeBundle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'anime.animeepisode': {
            'Meta': {'unique_together': "(('title', 'anime'),)", 'object_name': 'AnimeEpisode'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'animeepisodes'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'anime.animeepisodeauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'AnimeEpisodeAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_animeepisode_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_animeepisodes'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'anime.animeitem': {
            'Meta': {'ordering': "['title']", 'object_name': 'AnimeItem'},
            'air': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bundle': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'animeitems'", 'null': 'True', 'to': "orm['anime.AnimeBundle']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'endedAt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'endedKnown': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'episodesCount': ('django.db.models.fields.IntegerField', [], {}),
            'genre': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['anime.Genre']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'releaseType': ('django.db.models.fields.IntegerField', [], {}),
            'releasedAt': ('django.db.models.fields.DateTimeField', [], {}),
            'releasedKnown': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'anime.animeitemauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'AnimeItemAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_animeitem_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'air': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bundle': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_auditlog_animeitems'", 'null': 'True', 'to': "orm['anime.AnimeBundle']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'endedAt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'endedKnown': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'episodesCount': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'releaseType': ('django.db.models.fields.IntegerField', [], {}),
            'releasedAt': ('django.db.models.fields.DateTimeField', [], {}),
            'releasedKnown': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'anime.animelink': {
            'Meta': {'unique_together': "(('link', 'anime'),)", 'object_name': 'AnimeLink'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '100'}),
            'linkType': ('django.db.models.fields.IntegerField', [], {})
        },
        'anime.animelinkauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'AnimeLinkAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_animelink_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_links'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '100'}),
            'linkType': ('django.db.models.fields.IntegerField', [], {}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'anime.animename': {
            'Meta': {'ordering': "['title']", 'unique_together': "(('title', 'anime'),)", 'object_name': 'AnimeName'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'animenames'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'anime.animenameauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'AnimeNameAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_animename_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_animenames'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'anime.animerequest': {
            'Meta': {'object_name': 'AnimeRequest'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'requests'", 'null': 'True', 'to': "orm['anime.AnimeItem']"}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'requestType': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'anime.credit': {
            'Meta': {'object_name': 'Credit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'anime.genre': {
            'Meta': {'ordering': "['name']", 'object_name': 'Genre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        },
        'anime.organisation': {
            'Meta': {'object_name': 'Organisation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'anime.organisationauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'OrganisationAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_organisation_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'anime.organisationbundle': {
            'Meta': {'unique_together': "(('anime', 'organisation', 'job', 'role'),)", 'object_name': 'OrganisationBundle'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organisationbundles'", 'to': "orm['anime.AnimeItem']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['anime.Credit']"}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organisationbundles'", 'to': "orm['anime.Organisation']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        'anime.organisationbundleauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'OrganisationBundleAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_organisationbundle_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_organisationbundles'", 'to': "orm['anime.AnimeItem']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['anime.Credit']"}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_organisationbundles'", 'to': "orm['anime.Organisation']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        'anime.people': {
            'Meta': {'object_name': 'People'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'anime.peopleauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'PeopleAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_people_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'anime.peoplebundle': {
            'Meta': {'unique_together': "(('anime', 'person', 'job', 'role'),)", 'object_name': 'PeopleBundle'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'peoplebundles'", 'to': "orm['anime.AnimeItem']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['anime.Credit']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'peoplebundles'", 'to': "orm['anime.People']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        'anime.peoplebundleauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'PeopleBundleAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_peoplebundle_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_peoplebundles'", 'to': "orm['anime.AnimeItem']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['anime.Credit']"}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_peoplebundles'", 'to': "orm['anime.People']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        'anime.userstatusbundle': {
            'Meta': {'unique_together': "(('anime', 'user'),)", 'object_name': 'UserStatusBundle'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'statusbundles'", 'to': "orm['anime.AnimeItem']"}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '6', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['anime']
