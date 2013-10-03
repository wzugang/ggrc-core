/*
 * Copyright (C) 2013 Google Inc., authors, and contributors <see AUTHORS file>
 * Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 * Created By:
 * Maintained By:
 */

//= require can.jquery-all
//= require pbc/system
//= require pbc/population_sample
//= require pbc/meeting

can.Model.Cacheable("CMS.Models.Response", {

  root_object : "response"
  , root_collection : "responses"
  , subclasses : []
  , init : function() {
    this._super && this._super.apply(this, arguments);

    this.cache = {};
    if(this !== CMS.Models.Response) {
      CMS.Models.Response.subclasses.push(this);
    }
  }
  , create : "POST /api/responses"
  , update : "PUT /api/responses/{id}"

  , findAll : "GET /api/responses"
  , destroy : "DELETE /api/responses/{id}"
  , model : function(params) {
    var found = false;
    if (this.shortName !== 'Response')
      return this._super(params);
    if (!params)
      return params;
    params = this.object_from_resource(params);
    if (!params.selfLink) {
      if (params.type && params.type !== 'Response')
        return CMS.Models[params.type].model(params);
    } else {
      can.each(this.subclasses, function(m) {
        if(m.root_object === params.response_type) {
          params = m.model(params);
          found = true;
          return false;
        } else if(m.root_object in params) {
          params = m.model(m.object_from_resource(params));
          found = true;
          return false;
        }
      });
    }
    if(found) {
      return params;
    } else {
      console.debug("Invalid Response:", params);
    }
  }
  , attributes : {
    owner : "CMS.Models.Person.model"
    , object_people : "CMS.Models.ObjectPerson.stubs"
    , people : "CMS.Models.Person.stubs"
    , object_documents : "CMS.Models.ObjectDocument.stubs"
    , documents : "CMS.Models.Document.stubs"
    , population_sample : "CMS.Models.PopulationSample.stub"
    , meetings : "CMS.Models.Meeting.stubs"
    , participants : "CMS.Models.Person.stubs"
    , request : "CMS.Models.Request.stub"
    , assignee : "CMS.Models.Person.stub"
    , related_sources : "CMS.Models.Relationship.stubs"
    , related_destinations : "CMS.Models.Relationship.stubs"
  }
  , tree_view_options : {
    show_view : GGRC.mustache_path + "/responses/tree.mustache"
    , footer_view : GGRC.mustache_path + "/responses/tree_footer.mustache"
    , draw_children : true
    , child_options : [{
      //0: mapped objects
      mapping : "related_objects"
      , model : can.Model.Cacheable
      , show_view : GGRC.mustache_path + "/base_objects/tree.mustache"
      , footer_view : GGRC.mustache_path + "/base_objects/tree_footer.mustache"
      , allow_mapping : true
    }, {
      //1: Document Evidence
      model : "Document"
      , mapping : "documents"
    }, {
      //2: Meetings
      model : "Meeting"
      , show_view : GGRC.mustache_path + "/meetings/tree.mustache"
      , footer_view : GGRC.mustache_path + "/meetings/tree_footer.mustache"
    }, {
      //3: Meeting participants
      model : "Person"
    }]
  }
}, {
});

CMS.Models.Response("CMS.Models.DocumentationResponse", {
  root_object : "documentation_response"
  , root_collection : "documentation_responses"
  , create : "POST /api/documentation_responses"
  , update : "PUT /api/documentation_responses/{id}"
  , findAll : "GET /api/documentation_responses"
  , destroy : "DELETE /api/documentation_responses/{id}"
  , attributes : {}
  , init : function() {
    this._super && this._super.apply(this, arguments);
    can.extend(this.attributes, CMS.Models.Response.attributes);
    this.cache = CMS.Models.Response.cache;
  }
}, {});

CMS.Models.Response("CMS.Models.InterviewResponse", {
  root_object : "interview_response"
  , root_collection : "interview_responses"
  , create : "POST /api/interview_responses"
  , update : "PUT /api/interview_responses/{id}"
  , findAll : "GET /api/interview_responses"
  , destroy : "DELETE /api/interview_responses/{id}"
  , attributes : {}
  , init : function() {
    this._super && this._super.apply(this, arguments);
    can.extend(this.attributes, CMS.Models.Response.attributes);
    this.cache = CMS.Models.Response.cache;
  }
}, {});

CMS.Models.Response("CMS.Models.PopulationSampleResponse", {
  root_object : "population_sample_response"
  , root_collection : "population_sample_responses"
  , create : "POST /api/population_sample_responses"
  , update : "PUT /api/population_sample_responses/{id}"
  , findAll : "GET /api/population_sample_responses"
  , destroy : "DELETE /api/population_sample_responses/{id}"
  , attributes : {}
  , init : function() {
    this._super && this._super.apply(this, arguments);
    can.extend(this.attributes, CMS.Models.Response.attributes);
    this.cache = CMS.Models.Response.cache;
  }
}, {});